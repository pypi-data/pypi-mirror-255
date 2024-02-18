"""
Default Download runner

This module contains the LoggingDownloadRunner class. 

The LoggingDownloadRunner is responsible for running the JobDownloader or the DaemonDownloader. 
If there are no jobids, then the DaemonDownloader is used. 

It also registers callbacks that are called when certain events occur during the download. 
It uses these callbacks to display progress via the logging module and to report dopwnloaded status 
back to the server.

"""


import logging
from ciocore.downloader.download_runner_base import DownloadRunnerBase

LOG_FORMATTER = logging.Formatter(
    "%(asctime)s  %(name)s%(levelname)9s %(filename)s-%(lineno)d %(threadName)s:  %(message)s"
)

logger = logging.getLogger("conductor.logging_download_runner")

class LoggingDownloadRunner(DownloadRunnerBase):
    CLIENT_NAME = "LoggingDownloadRunner"

    def __init__(self, jobids=None, location=None, **kwargs):

        super().__init__(jobids, location, **kwargs)
        
        logger.debug("Assigning callbacks")
        self.downloader.on("start", self.on_start)
        self.downloader.on("start_task", self.on_start_task)
        self.downloader.on("progress", self.on_progress)
        self.downloader.on("file_done", self.on_file_done)
        self.downloader.on("task_done", self.on_task_done)
        self.downloader.on("done", self.on_done)

    # Callbacks
    def on_start(self, evt):
        logger.info("Starting download")

    def on_start_task(self, evt):
        logger.info(f"Starting task {evt['job_id']}:{evt['task_id']}")

    def on_progress(self, evt):
        percent = 0
        if evt["size"] and evt["progress_bytes"]:
            percent = round(evt["progress_bytes"] / evt["size"] * 100, 2)
        logger.info(f"Progress: {evt['filepath']} {percent}%")

    def on_file_done(self, evt):
        msg = f"File done {evt['job_id']}:{evt['task_id']}:{evt['filepath']}"
        if evt["error"]:
            msg += f" {evt['error']}"
        logger.info(msg)

    def on_task_done(self, evt):
        if evt["preexisting"]:
            logger.info(
                f"Task already existed locally {evt['job_id']}:{evt['task_id']}"
            )
        else:
            logger.info(f"Task done {evt['job_id']}:{evt['task_id']}")
            

    def on_done(self, evt):
        """
        When the job is done, check to see if any tasks were not completed.

        If we find any, then report them as pending.
        """
        logger.info("Download done")
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

        if messages:
            logger.warning("Some tasks were not completed:")
            for message in messages:
                logger.warning(message)
