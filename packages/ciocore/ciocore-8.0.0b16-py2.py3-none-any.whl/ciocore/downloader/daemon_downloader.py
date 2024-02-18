"""
Daemon Downloader

Not yet tested
"""
import json
import logging
import time
from ciocore.downloader.base_downloader import BaseDownloader

logger = logging.getLogger("conductor.daemon_downloader")

class DaemonDownloader(BaseDownloader):
    CLIENT_NAME = "DaemonDownloader"
    POLL_INTERVAL = 15
    URL = "/downloads/next"

    def __init__(self, location, *args, **kwargs):
        """Initialize the downloader."""
        super().__init__(*args, **kwargs)
        self.location = location
        logger.debug("Initializing daemon downloader")

    def get_some_tasks(self, _):
        """Fetch the next batch of tasks from the server.
        """
        logger.debug(f"Fetching the next page of tasks")
        params = {"count": self.page_size, "location": self.location}
        while True:
            response, code = self.client.make_request(
                self.URL, params=params, use_api_key=True
            )
            if code <= 201:
                tasks = json.loads(response).get("data", [])
                if tasks:
                    return tasks, True
            elif code == 204:
                logger.warning(f"Listening for files to download...")
            else:
                logger.error(f"Error downloading task info from: {self.URL}")

            time.sleep(self.POLL_INTERVAL)

