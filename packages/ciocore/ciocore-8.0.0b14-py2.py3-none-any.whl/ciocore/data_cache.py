"""
Maintain a cache of data from the conductor API.

Currently covers projects, instance types, and software packages. Data is stored in
a TinyDB database under the user's Companion data directory, or a chosen directory. 

The cache is considered stale after 24 hours.
"""

import os
import sys
import errno
from ciocore import api_client
from tinydb import TinyDB, Query
import time
from contextlib import contextmanager

PLATFORM = sys.platform
SECONDS_TO_EXPIRE = 86400


class DataCache(object):
    SCHEMA_VERSION = 1

    def __init__(self, db_location=None):
        self.db_path = _get_path(db_location)
        self._ensure_path()
        self._ensure_db_tables()
        self.db = None
        
    @contextmanager
    def database(self):
        self.db = TinyDB(self.db_path)
        try:
            yield self.db
        finally:
            self.db.close()
            
    def _ensure_db_tables(self):
        with self.database() as db:
            db.table("projects")
            db.table("instance_types")
            db.table("packages")
            db.table("metadata")

    def _ensure_path(self):
        dir_path = os.path.dirname(self.db_path)
        try:
            os.makedirs(os.path.dirname(dir_path))
        # catch either FileExistsError or OSError
        except FileExistsError:
            pass 
        except OSError as ex:
            if ex.errno == errno.EEXIST and os.path.isdir(dir_path):
                pass
            else:
                raise

    def _fetch_resources(self, account_id):
        self._fetch_projects(account_id)
        self._fetch_instance_types(account_id)
        self._fetch_packages()
        self.db.table("metadata").upsert(
            {
                "updated_at": int(time.time()),
                "account_id": account_id,
                "schema_version": self.SCHEMA_VERSION,
            },
            Query().doc_id == 1,
        )

    def _fetch_projects(self, account_id):
        """
        Fetch projects from the API and store them in the database.

        Each list of projects is stored with an account_id to account for users with multiple
        accounts.
        """
        # self._set_schema_version()
        projects = api_client.request_projects()

        self.db.table("projects").upsert(
            {"account_id": account_id, "data": projects},
            Query().account_id == account_id,
        )

    def _fetch_instance_types(self, account_id):
        """
        Fetch instance types from the API and store them in the database.

        Like projects, each list of instance types is stored with an account_id.
        """
        instance_types = api_client.request_instance_types()
        # add account_id to each instance type
        self.db.table("instance_types").upsert(
            {
                "account_id": account_id,
                "data": instance_types,
            },
            Query().account_id == account_id,
        )

    def _fetch_packages(self):
        """
        Fetch software packages from the API and store them in the database.
        """
        packages = api_client.request_software_packages()
        table = self.db.table("packages")
        table.truncate()
        table.insert({"data": packages})

    def _needs_refresh(self, account_id):
        metadata = self.db.table("metadata").get(doc_id=1)
        if not metadata:
            return True
        if "updated_at" not in metadata:
            return True
        if "schema_version" not in metadata:
            return True
        if metadata["schema_version"] != self.SCHEMA_VERSION:
            return True
        if (int(time.time()) - metadata["updated_at"]) > SECONDS_TO_EXPIRE:
            return True

        for table_name in ["projects", "instance_types"]:
            entry = self.db.table(table_name).get(Query().account_id == account_id)
            if not entry:
                return True
        packages = self.db.table("packages").get(doc_id=1)
        if not packages:
            return True
        return False

    def _ensure_resources(self, account_id=None):
        if self._needs_refresh(account_id):
            self._fetch_resources(account_id)

    ############### PUBLIC API #####################
    def get_data(self, account_id):
        """
        Get all data from the cache or the API.
        """
        with self.database():
            self._ensure_resources(account_id)
            projects = self.db.table("projects").get(Query().account_id == account_id)
            instance_types = self.db.table("instance_types").get(
                Query().account_id == account_id
            )
            packages = self.db.table("packages").get(doc_id=1)

            return {
                "projects": projects and projects["data"],
                "instance_types": instance_types and instance_types["data"],
                "packages": packages and packages["data"],
            }

    def get_projects(self, account_id):
        """
        Get projects from the cache or the API.
        """
        with self.database():
            self._ensure_resources(account_id)
            projects = self.db.table("projects").get(Query().account_id == account_id)
            return projects and projects["data"]

    def get_instance_types(self, account_id):
        """
        Get instance types from the cache or the API.
        """
        with self.database():
            self._ensure_resources(account_id)
            instance_types = self.db.table("instance_types").get(
                Query().account_id == account_id
            )
            return instance_types and instance_types["data"]

    def get_packages(self):
        """
        Get software packages from the cache or the API.
        """
        with self.database():
            self._ensure_resources()
            packages = self.db.table("packages").get(doc_id=1)
            return packages and packages["data"]

    def clear(self):
        """
        Clear out data.
        """
        with self.database() as db:
            for table_name in ["projects", "instance_types", "packages"]:
                self.db.table(table_name).truncate()


def _get_path(db_location=None):
    env_value = os.environ.get("CONDUCTOR_TINYDB_LOCATION")

    if db_location:
        root = db_location
    elif env_value:
        root = env_value
    elif PLATFORM.startswith("darwin"):
        root = "~/Library/Application Support/conductor-companion/Default/"
    elif PLATFORM.startswith("linux"):
        root = "~/.config/conductor-companion/User Data/Default/"
    elif PLATFORM.startswith("win"):
        root = "%LOCALAPPDATA%/conductor-companion/User Data/Default/"
    else:
        root = "~/Conductor/"

    return os.path.expandvars(
        os.path.expanduser(os.path.join(root, "TinyDB", "resources.json"))
    )
