"""
Base Download runner

This module contains the DownloadRunnerBase class. 

The DownloadRunnerBase is responsible for running one of the downloader classes: JobDownloader or DaemonDownloader. If there are no jobids, then it runs the DaemonDownloader. 

It registers callbacks with the with the the Downloader that allow it to report "downloaded" or "pending" status back to the server.

Derived classses can avoid the complexities of threading contained in this class and the base downloader. They can register their own callbacks and know that they are running in the main thread. 

For an example of a derived class, see LoggingDownloadRunner.
"""

import json
import logging
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import threading
from ciocore import api_client
from ciocore.downloader.job_downloader import JobDownloader
from ciocore.downloader.daemon_downloader import DaemonDownloader

LOG_FORMATTER = logging.Formatter(
    "%(asctime)s  %(name)s%(levelname)9s %(filename)s-%(lineno)d %(threadName)s:  %(message)s"
)

STATUS_ENDPOINT = "/downloads/status"

STATUS_DOWNLOADED = "downloaded"
STATUS_PENDING = "pending"

logger = logging.getLogger("conductor.default_download_runner")

callback_queue = Queue()


class DownloadRunnerBase(object):
    CLIENT_NAME = "DownloadRunnerBase"

    # A flag that can be seen by all threads. When set, the threads will stop.
    interrupt_flag = threading.Event()

    def __init__(self, jobids=None, location=None, **kwargs):
        if jobids:
            self.downloader = JobDownloader(jobids, **kwargs)
        else:
            self.downloader = DaemonDownloader(location, **kwargs)

        self.num_threads = kwargs.get("num_threads", 1)
        self.client = api_client.ApiClient()
        self.reporter = None

        # These callbacks are prefixed `base_` to avoid name collisions with derived classes.
        logger.debug("Assigning callbacks")
        self.downloader.on("start", self.base_on_start)
        self.downloader.on("start_task", self.base_on_start_task)
        self.downloader.on("file_done", self.base_on_file_done)
        self.downloader.on("task_done", self.base_on_task_done)
        self.downloader.on("done", self.base_on_done)

    def run(self):
        """
        Run the downloader.

        Start a reporter thread to report task status back to the server.
        """
        DownloadRunnerBase.interrupt_flag.clear()
        try:
            self.reporter = ThreadPoolExecutor(max_workers=self.num_threads)
            self.downloader.run()
        except KeyboardInterrupt:
            DownloadRunnerBase.interrupt_flag.set()
        except Exception as e:
            logger.exception(f"Error running downloader: {e}")
        finally:
            self.reporter.shutdown()

    def report_task_status(
        self, download_id, status=STATUS_DOWNLOADED, bytes_in_task=0
    ):
        # If the user iunterrupted the download, then we're just going to set the task status
        # back to pending to be safe. So what if they have to dl one or two files again?
        if DownloadRunnerBase.interrupt_flag.is_set():
            status = STATUS_PENDING

        bytes_to_download = 0 if status == STATUS_DOWNLOADED else bytes_in_task

        data = {
            "download_id": download_id,
            "status": status,
            "bytes_downloaded": 0,
            "bytes_to_download": bytes_to_download,
        }
        json_data = json.dumps(data)

        self.client.make_request(STATUS_ENDPOINT, data=json_data, use_api_key=True)

        return data

    # Callbacks
    def base_on_start(self, evt):
        logger.debug("Starting download")

    def base_on_start_task(self, evt):
        logger.debug(f"Starting task {evt['job_id']}:{evt['task_id']}")
        
    def base_on_file_done(self, evt):
        msg = f"File done {evt['job_id']}:{evt['task_id']}:{evt['filepath']}"
        if evt["error"]:
            msg += f" {evt['error']}"
        logger.debug(msg)

    def base_on_task_done(self, evt):
        if evt["preexisting"]:
            logger.debug(
                f"Task already existed locally {evt['job_id']}:{evt['task_id']}"
            )
            return
        future = self.reporter.submit(
            self.report_task_status,
            evt["download_id"],
            status=STATUS_DOWNLOADED,
            bytes_in_task=evt["size"],
        )
        future.add_done_callback(
            lambda f: log_actual_report_result(
                f.result(), evt["job_id"], evt["task_id"]
            )
        )

    def base_on_done(self, evt):
        """
        When the job is done, check to see if any tasks were not completed.

        If we find any, then report them as pending.
        """
        logger.debug(f"Download done")
        messages = []
        for job_id in evt["registry"]:
            job = evt["registry"][job_id]
            for task_id in job:
                task = job[task_id]

                if task['completed_files'] >= task['filecount']:
                    # This should never happen since completed tasks are removed from the
                    # registry as part of the on_task_done callback.
                    continue

                messages.append(
                    f"Task not completed {job_id}:{task_id}: {task['completed_files']}/{task['filecount']} files."
                )
                future = self.reporter.submit(
                    self.report_task_status,
                    task['download_id'],
                    status=STATUS_PENDING,
                    bytes_in_task=task['size'],
                )
                future.add_done_callback(
                    lambda f: log_actual_report_result(f.result(), job_id, task_id)
                )

        if messages:
            logger.warning("Some tasks were not completed:")
            for message in messages:
                logger.warning(message)


def log_actual_report_result(report_result, job_id, task_id):
    """Log the report.

    It's possible the report back to the server was changed by the report_task_status, for example
    if the user interrupted the download.

    For this reason we log the actual report result.
    """
    msg = f"Reported task {report_result['status']} {job_id}:{task_id} ({report_result['download_id']})"
    if report_result["status"] == STATUS_DOWNLOADED:
        logger.debug(msg)
    else:
        logger.warning(msg)
