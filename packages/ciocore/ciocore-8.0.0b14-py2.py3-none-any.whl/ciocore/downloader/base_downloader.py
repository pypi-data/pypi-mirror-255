"""
Contains the base class for both the JobDownloader and the DaemonDownloader.


PAGING
Both the job downloader and the daemon downloader get their lists of tasks to download in batches. In both cases they implement the get_some_tasks() method. This method is called repeatedly until it is interrupted or until it returns a falsy locator. The locator, if not falsy, is whatever the derived class finds useful. See the documentation for the derived classes for detailed information.

CALLBACKS
The intention is to keep the downloader simple and flexible. As such, some functionality is intentionally left out. For example, we do not report back to the Conductor API when tasks are complete. We do not format output, other than that provided by standard logging. We do not provide a GUI. Instead, we emit lifecycle events that can be used to do all of these things and more. The LoggingDownloadRunner class demonstrates this.

Callbacks are called with an 'evt' argument, which is a dictionary containing information about the event. The events are listed in the VALID_EVENTS list. To register a callback you use the `on` method - for example: `downloader.on("start", my_callback)`. The callback must be a function that accepts one argument named 'evt'. The callback can be a method of another class. Several callbacks may be registered for the same event type.

Since the downloader is multithreaded, the events are generated in different threads. We use a Queue to pass the events from the downloader threads to the main thread. The method, dispatch_events is responsible for reading events from the queue and calling the appropriate callbacks. 

Most event types are emitted unchanged as they are received from the queue. However, if one or more callbacks are registered to handle the EVENT_TYPE_TASK_DONE event, then the dispatch_events method will also generate a TASK_DONE event when all files for a task have been downloaded. In order to do this, it keeps a registry of tasks and the number of files downloaded for each task. When the number of files downloaded equals the number of files to download, the task is considered done, and at this point we emit the event and delete the task from the registry. Tasks in the registry are grouped under their job_id.

RETRIES
If an error occurs during download, the file will be retried with exponential backoff and jitter. We do not retry however when the download is interrupted by the user.

MD5 HASHES
If force is False, and a file already exists on disk, the md5 hash of the file is compared to the md5 hash of the file on the server. If the hashes match, the file is skipped.
If force is True, then the file is downloaded regardless.

FILTERING
The regex parameter can be used to filter the files that are downloaded. If the regex parameter is provided, only files whose relative path matches the regex using `re.search` will be downloaded. This means users can give a literal string and the downloader will download all files whose relative path contains that string.
"""


import base64
import contextlib
import hashlib
import logging
import os
import random
import re
import shutil
import stat
import tempfile
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

import requests
from ciocore import api_client

LOG_FORMATTER = logging.Formatter(
    "%(asctime)s  %(name)s%(levelname)9s %(filename)s-%(lineno)d %(threadName)s:  %(message)s"
)

logger = logging.getLogger("conductor.base_downloader")

DEFAULT_PAGE_SIZE = 50
DEFAULT_NUM_THREADS = 4
DEFAULT_PROGRESS_INTERVAL = 0.5
CHUNK_SIZE = 1024
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_DELAY = 1
DEFAULT_JITTER = 0.1

EVENT_TYPE_START = "start"
EVENT_TYPE_START_TASK = "start_task"
EVENT_TYPE_FILE_DONE = "file_done"
EVENT_TYPE_TASK_DONE = "task_done"
EVENT_TYPE_DONE = "done"
EVENT_TYPE_PROGRESS = "progress"


class UserInterrupted(Exception):
    pass


@contextlib.contextmanager
def temp_file(filepath):
    """Create a temporary file to use instead of the input filepath.

    The input doesn't have to exist. If it does exist, it will ultimately be overwritten.
    """
    try:
        dirpath, filename = os.path.split(filepath)
        # ensure the directory exists
        os.makedirs(dirpath, exist_ok=True)
        temp_file_desc = tempfile.mkstemp(prefix=filename, dir=dirpath)
        temp_file_path = temp_file_desc[1]
        os.close(temp_file_desc[0])
        yield temp_file_path

        shutil.move(temp_file_path, filepath)
        os.chmod(
            filepath,
            stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH,
        )
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


class BaseDownloader(object):
    CLIENT_NAME = "BaseDownloader"
    WORK_QUEUE_THROTTLE = 0.1
    EVENT_DISPATCHER_PAUSE = 0.1

    interrupt_flag = threading.Event()

    VALID_EVENTS = [
        EVENT_TYPE_START,
        EVENT_TYPE_START_TASK,
        EVENT_TYPE_PROGRESS,
        EVENT_TYPE_TASK_DONE,
        EVENT_TYPE_FILE_DONE,
        EVENT_TYPE_DONE,
    ]

    @contextlib.contextmanager
    def start_end_events(self):
        """Send start and end events to the event queue."""
        self.emit_start_event()
        try:
            yield
        finally:
            self.emit_end_event()

    def __init__(
        self,
        destination=None,
        num_threads=DEFAULT_NUM_THREADS,
        progress_interval=DEFAULT_PROGRESS_INTERVAL,
        page_size=DEFAULT_PAGE_SIZE,
        force=False,
        regex=None,
        max_attempts=DEFAULT_MAX_ATTEMPTS,
        delay=DEFAULT_DELAY,
        jitter=DEFAULT_JITTER,
    ):
        """Initialize the downloader."""
        logger.debug("Initializing paged job downloader")
        self.destination = destination
        self.force = force
        self.num_threads = num_threads
        self.max_queue_size = num_threads * 2
        self.progress_interval = progress_interval / 1000.0
        self.page_size = page_size if page_size > 1 else None
        self.client = api_client.ApiClient()
        self.max_attempts = max_attempts
        self.delay = delay
        self.jitter = jitter
        self.regex = re.compile(regex) if regex else None

        self.event_queue = None

        self.callbacks = {
            EVENT_TYPE_START: [],
            EVENT_TYPE_START_TASK: [],
            EVENT_TYPE_PROGRESS: [],
            EVENT_TYPE_TASK_DONE: [],
            EVENT_TYPE_FILE_DONE: [],
            EVENT_TYPE_DONE: [],
        }

        # A registry of tasks that are in progress. When a task is done, it is removed from the registry.
        self.registry = {}

        logger.debug("Destination: %s", self.destination)
        logger.debug("Force download: %s", self.force)
        logger.debug("Num threads: %s", self.num_threads)
        logger.debug("Max queue size: %s", self.max_queue_size)
        logger.debug("Progress interval: %s seconds", self.progress_interval)
        logger.debug("Page limit: %s", self.page_size)
        logger.debug("Instantiated client: %s", self.client)
        logger.debug("Max attempts: %s", self.max_attempts)
        logger.debug("Delay: %s", self.delay)
        logger.debug("Jitter: %s", self.jitter)

    def run(self):
        """Run the downloader.

        For each job, we request pages of tasks, and then download each file from each task in a
        thread.
        """
        logger.debug("Running job downloader")
        BaseDownloader.interrupt_flag.clear()

        self.event_queue = Queue()
        event_dispatcher_thread = threading.Thread(target=self.dispatch_events)
        event_dispatcher_thread.start()

        with self.start_end_events():

            # Run a loop that fetches pages of tasks from the server.
            # next_locator can be determined by the implementation of get_some_tasks(). 
            # It is fed in and returned each loop. 
            # If it is returned as None, the loop will end.

            try:
                with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                    next_locator = None
                    while True:
                        tasks, next_locator = self.get_some_tasks(next_locator)
                        if tasks:
                            self.download_tasks(tasks, executor)
                        if not next_locator:
                            break
            except KeyboardInterrupt:
                # Let the workers know they should stop
                logger.warning(
                    "Keyboard interrupt received. Cleaning up. Please be patient..."
                )
                BaseDownloader.interrupt_flag.set()

            executor.shutdown()

        # IMPORTANT
        event_dispatcher_thread.join()

    def get_some_tasks(self, locator):
        """Get a page of tasks from the server."""
        raise NotImplementedError

    def download_tasks(self, tasks, executor):
        """Run a single page of tasks."""
        logger.debug(f"Downloading page:")

        for task_info in tasks:
            self.emit_start_task_event(task_info)
            for file_info in task_info["files"]:
                if self.regex:
                    if not self.regex.search(file_info["relative_path"]):
                        continue
                if self.destination:
                    file_info["output_dir"] = os.path.join(
                        self.destination, task_info["job_id"]
                    )
                file_info["filepath"] = os.path.join(
                    file_info["output_dir"], file_info["relative_path"]
                )

                # Attempt to download the file in a thread. When the download is complete, the result will be put in the event queue.
                future = executor.submit(self.attempt_download, file_info)
                future.add_done_callback(lambda f: self.event_queue.put(f.result()))
                while executor._work_queue.qsize() > self.max_queue_size:
                    # Throttle to prevent the queue from growing too large.
                    time.sleep(self.WORK_QUEUE_THROTTLE)

        # finished submitting the batch. It doesn't mean the batch is done downloading.

    def attempt_download(self, file_info):
        """Attempt to download a file with exponential backoff retries."""
        filepath = file_info["filepath"]

        attempts = self.max_attempts
        retries_delay = self.delay
        try_again = True
        while try_again:
            try:
                file_done_event = self.download(file_info)
                return file_done_event
            except UserInterrupted as ex:
                try_again = False
                file_done_event = self.generate_file_done_event(
                    file_info, error=str(ex)
                )
            except Exception as ex:
                attempts -= 1
                if attempts <= 0:
                    try_again = False
                    traceback_str = traceback.format_exc()
                    error_str = f"{ex}\nTraceback:\n{traceback_str}"
                    file_done_event = self.generate_file_done_event(
                        file_info, error=error_str
                    )
                    msg = f"Failed download {filepath} and exhausted {self.max_attempts} attempts."
                else:
                    time.sleep(retries_delay)
                    retries_delay = retries_delay * 2 + random.uniform(
                        0, retries_delay * self.jitter
                    )
                    msg = f"Failed download {filepath} and will try {attempts} more times in {retries_delay} seconds."
                logger.exception(msg)

        return file_done_event

    def can_skip(self, file_info):
        """Determine if a file should be skipped."""

        if self.force:
            return False

        filepath = file_info["filepath"]
        if not os.path.exists(filepath):
            return False
        try:
            existing_md5 = _generate_base64_md5(filepath)
            download_md5 = file_info.get("md5")
            if existing_md5 != download_md5:
                return False
        except Exception:
            logger.exception(f"Error checking md5 for {filepath}")
            return False

        return self.generate_file_done_event(file_info, preexisting=True)

    def download(self, file_info):
        """
        Do the work of downloading a file.

        Use a temp file to avoid corrupting the original file if the download fails.
        """
        skip_result = self.can_skip(file_info)
        if skip_result:
            return skip_result

        size = file_info["size"]
        filepath = os.path.join(file_info["output_dir"], file_info["relative_path"])

        logger.debug(f"Downloading file: {filepath}")

        with temp_file(filepath) as safe_filepath:
            response = requests.get(file_info["url"], stream=True, timeout=60)
            size = float(response.headers.get("content-length", 0))
            progress_bytes = 0
            last_poll = time.time()
            with open(safe_filepath, "wb") as file_handle:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    # check if the download has been interrupted
                    if BaseDownloader.interrupt_flag.is_set():
                        # break

                        raise UserInterrupted("Download interrupted by user.")

                    if not chunk:
                        continue
                    file_handle.write(chunk)

                    progress_bytes += len(chunk)
                    last_poll = self.emit_progress_event(
                        filepath, progress_bytes, size, last_poll
                    )

            response.raise_for_status()

        return self.generate_file_done_event(file_info)

    def dispatch_events(self):
        """
        Pull events from the event queue as they are ready and call the appropriate callbacks.
        """
        while True:
            if self.event_queue.empty():
                time.sleep(self.EVENT_DISPATCHER_PAUSE)
                continue
            evt = self.event_queue.get(timeout=1)

            event_type = evt["type"]

            for callback in self.callbacks[event_type]:
                callback(evt)

            if len(self.callbacks[EVENT_TYPE_TASK_DONE]):
                task_done_event = self.get_task_done_event(evt)
                if task_done_event:
                    for callback in self.callbacks[EVENT_TYPE_TASK_DONE]:
                        callback(task_done_event)

            if event_type == EVENT_TYPE_DONE:
                break

    def get_task_done_event(self, evt):
        """
        If the event is a file_done event, check if the whole task is done. If so, return a task_done event.

        We also detect task start events as they are required for building the data structure that we use to determine if a task is done.

        """
        event_type = evt["type"]

        if event_type == EVENT_TYPE_START_TASK:
            # Start building the nested dict for this task [job_id][task_id]
            job_id = evt["job_id"]
            task_id = evt["task_id"]
            if job_id not in self.registry:
                self.registry[job_id] = {}
            self.registry[job_id][task_id] = {
                "download_id": evt["download_id"],
                "filecount": evt["filecount"],
                "completed_files": 0,
                "preexisting_files": 0,
                "size": evt["size"],
            }
        elif event_type == EVENT_TYPE_FILE_DONE:
            # Increment the number of downloaded files for the task
            err = evt.get("error")
            if not err:
                job_id = evt["job_id"]
                task_id = evt["task_id"]
                registered_task = self.registry[job_id][task_id]
                registered_task["completed_files"] += 1
                registered_task["preexisting_files"] += 1 if evt["preexisting"] else 0
                if registered_task["completed_files"] >= registered_task["filecount"]:
                    task_done_event = {
                        "type": EVENT_TYPE_TASK_DONE,
                        "job_id": job_id,
                        "task_id": task_id,
                        "download_id": registered_task["download_id"],
                        "filecount": registered_task["filecount"],
                        "preexisting": registered_task["preexisting_files"]
                        == registered_task["filecount"],
                        "size": registered_task["size"],
                    }
                    del self.registry[job_id][task_id]
                    return task_done_event
        return None

    ############## METHODS TO CONSTRUCT EVENTS #####################
    def emit_start_task_event(self, task):
        """Send a start_task event to the event queue."""
        self.event_queue.put(
            {
                "type": EVENT_TYPE_START_TASK,
                "download_id": task["download_id"],
                "filecount": len(task["files"]),
                "task_id": task["task_id"],
                "job_id": task["job_id"],
                "size": task["size"],
            }
        )

    def emit_progress_event(self, filepath, progress_bytes, size, last_poll):
        now = time.time()
        if now >= last_poll + self.progress_interval:
            last_poll = now
            self.event_queue.put(
                {
                    "type": EVENT_TYPE_PROGRESS,
                    "filepath": filepath,
                    "progress_bytes": progress_bytes,
                    "size": size,
                }
            )
        return last_poll

    def emit_start_event(self):
        """Send start and end events to the event queue."""
        self.event_queue.put(
            {
                "type": EVENT_TYPE_START,
                "num_threads": self.num_threads,
                "page_size": self.page_size,
            }
        )

    def emit_end_event(self):
        self.event_queue.put({"type": EVENT_TYPE_DONE, "registry": self.registry})

    @staticmethod
    def generate_file_done_event(file, **kwargs):
        result = {
            "type": EVENT_TYPE_FILE_DONE,
            "job_id": file["job_id"],
            "task_id": file["task_id"],
            "filepath": file["filepath"],
            "md5": file["md5"],
            "size": file["size"],
            "preexisting": False,
            "error": None,
        }
        return {**result, **kwargs}

    ################################################################

    def on(self, event_type, callback):
        """Register a callback function.

        Args:
            event_type (str): The name of the callback. Must be one of the values in VALID_EVENTS.
            callback (function): The callback function. Must accept one argument named 'evt'.
        Raises:
            ValueError: If the event_type is not in VALID_EVENTS.

        Examples:
            >>> def my_callback(evt):
            ...     print(evt)

            >>> downloader = BaseDownloader(jobs)
            >>> downloader.on("start", my_callback)

        """
        if event_type not in self.VALID_EVENTS:
            raise ValueError(
                f"Invalid event_type: {event_type}. Allowed values: {self.VALID_EVENTS}"
            )
        _validate_callback(callback)
        self.callbacks[event_type].append(callback)


def _validate_callback(callback):
    """Make sure the callback is a callable function with one argument named 'evt'.

    The callback could be a method of another class, in which case the first argument will be 'self'. We account for this too.
    """
    if not callable(callback):
        raise ValueError("Callback must be a callable function.")
    num_args = callback.__code__.co_argcount

    arg_names = callback.__code__.co_varnames[:num_args]

    if num_args > 2 or (num_args == 2 and arg_names[0] != "self"):
        raise ValueError(f"Too many args. Found {num_args} arguments: {arg_names}")

    if num_args < 1 or arg_names[-1] != "evt":
        raise ValueError("Callback is missing the named argument 'evt'.")
    return True


def _generate_base64_md5(filename):
    with open(filename, "rb") as file:
        md5_hash = hashlib.md5()
        for chunk in iter(lambda: file.read(4096), b""):
            md5_hash.update(chunk)
        md5_digest = md5_hash.digest()
        md5_base64 = base64.b64encode(md5_digest)
        return md5_base64.decode("utf-8")
