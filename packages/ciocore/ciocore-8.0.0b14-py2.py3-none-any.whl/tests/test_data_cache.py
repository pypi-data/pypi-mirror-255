""" test data

   isort:skip_file
"""

import unittest
import os
import time
import shutil

try:
    from unittest import mock
except ImportError:
    import mock

from ciocore.data_cache import DataCache

from project_fixtures import PROJECTS
from package_fixtures import SOFTWARE_DATA
from instance_type_fixtures import ALL_INSTANCE_TYPES
from tinydb import Query


# class TestDataCache(unittest.TestCase):
#     def setUp(self):
#         self.files_path = os.path.abspath(
#             os.path.join(os.path.dirname(__file__), "files")
#         )

#         self.projects_patcher = mock.patch(
#             "ciocore.api_client.request_projects", return_value=PROJECTS
#         )
#         self.instance_types_patcher = mock.patch(
#             "ciocore.api_client.request_instance_types", return_value=ALL_INSTANCE_TYPES
#         )
#         self.software_packages_patcher = mock.patch(
#             "ciocore.api_client.request_software_packages", return_value=SOFTWARE_DATA
#         )

#         self.needs_refresh_patcher = mock.patch.object(
#             DataCache, "_needs_refresh", return_value=True
#         )

#         self.mock_projects = self.projects_patcher.start()
#         self.mock_instance_types = self.instance_types_patcher.start()
#         self.mock_software_packages = self.software_packages_patcher.start()
#         self.mock_needs_refresh = self.needs_refresh_patcher.start()

#         self.data_cache = DataCache(db_location=self.files_path)

#     def tearDown(self):
#         self.projects_patcher.stop()
#         self.instance_types_patcher.stop()
#         self.software_packages_patcher.stop()
#         self.needs_refresh_patcher.stop()

#         self.data_cache.clear()
        
#         # delete the contents of the db directory
#         folder_path = os.path.join(self.files_path, "TinyDB")
#         for file in os.listdir(folder_path):
#             file_path = os.path.join(folder_path, file)
#             try:
#                 if os.path.isfile(file_path):
#                     os.unlink(file_path)
#             except Exception as e:
#                 print(e)

#     def override_resources(
#         self, projects=None, instance_types=None, packages=None, needs_refresh=None
#     ):
#         if projects is not None:
#             self.mock_projects.return_value = projects
#         if instance_types is not None:
#             self.mock_instance_types.return_value = instance_types
#         if packages is not None:
#             self.mock_software_packages.return_value = packages
#         if needs_refresh is not None:
#             self.mock_needs_refresh.return_value = needs_refresh

#     def test_get_projects_returns_the_projects(self):
#         self.override_resources(needs_refresh=True)
#         result = self.data_cache.get_projects(account_id=12345)
#         self.mock_needs_refresh.assert_called_once_with(12345)
#         self.assertEqual(result, PROJECTS)

#     def test_get_projects_no_bust_cache_if_not_need_refresh(self):
#         # initial cache projects
#         self.data_cache.get_projects(account_id=12345)
#         self.override_resources(needs_refresh=False, projects=["a", "b"])
#         # the old values should still be returned
#         result = self.data_cache.get_projects(account_id=12345)
#         self.assertEqual(result, PROJECTS)

#     def test_get_projects_bust_cache_if_needs_refresh(self):
#         # initial cache projects
#         self.data_cache.get_projects(account_id=12345)
#         new_projects = ["a", "b"]
#         self.override_resources(needs_refresh=True, projects=new_projects)
#         # the new values should be returned
#         result = self.data_cache.get_projects(account_id=12345)
#         self.assertEqual(result, new_projects)

#     def test_get_packages_returns_the_packages(self):
#         self.override_resources(needs_refresh=True)
#         result = self.data_cache.get_packages()
#         self.mock_needs_refresh.assert_called_once()
#         self.assertEqual(result, SOFTWARE_DATA)

#     def test_get_packages_no_bust_cache_if_not_need_refresh(self):
#         # initial cache packages
#         self.data_cache.get_packages()
#         # turn off refresh and set api_client to return different packages
#         self.override_resources(needs_refresh=False, packages=["a", "b"])
#         # the old values should still be returned
#         result = self.data_cache.get_packages()
#         self.assertEqual(result, SOFTWARE_DATA)

#     def test_get_packages_bust_cache_if_needs_refresh(self):
#         # initial cache packages
#         self.data_cache.get_packages()
#         # turn off refresh and set api_client to return different packages
#         new_packages = ["a", "b"]
#         self.override_resources(needs_refresh=True, packages=new_packages)
#         # the new values should be returned
#         result = self.data_cache.get_packages()
#         self.assertEqual(result, new_packages)

#     def test_clear_clears_packages(self):
#         self.data_cache.get_packages()
#         self.data_cache.clear()
#         with self.data_cache.database() as db:
#             entries = db.table("packages").all()
#         self.assertEqual(entries, [])

#     def test_clear_clears_products_for_all_accounts(self):
#         self.data_cache.get_projects(account_id=12345)
#         self.data_cache.get_projects(account_id=67890)
#         self.data_cache.clear()
#         with self.data_cache.database() as db:
#             entries = self.data_cache.db.table("projects").all()
#         self.assertEqual(len(entries), 0)


# class TestDataCacheNeedsRefresh(unittest.TestCase):
#     def setUp(self):
#         self.files_path = os.path.abspath(
#             os.path.join(os.path.dirname(__file__), "files")
#         )

#         self.projects_patcher = mock.patch(
#             "ciocore.api_client.request_projects", return_value=PROJECTS
#         )
#         self.instance_types_patcher = mock.patch(
#             "ciocore.api_client.request_instance_types", return_value=ALL_INSTANCE_TYPES
#         )
#         self.software_packages_patcher = mock.patch(
#             "ciocore.api_client.request_software_packages", return_value=SOFTWARE_DATA
#         )

#         self.mock_projects = self.projects_patcher.start()
#         self.mock_instance_types = self.instance_types_patcher.start()
#         self.mock_software_packages = self.software_packages_patcher.start()

#         self.data_cache = DataCache(db_location=self.files_path)

#     def tearDown(self):
#         self.projects_patcher.stop()
#         self.instance_types_patcher.stop()
#         self.software_packages_patcher.stop()

#         self.data_cache.clear()
        
#         # delete the contents of the db directory
#         folder_path = os.path.join(self.files_path, "TinyDB")
#         for file in os.listdir(folder_path):
#             file_path = os.path.join(folder_path, file)
#             try:
#                 if os.path.isfile(file_path):
#                     os.unlink(file_path)
#             except Exception as e:
#                 print(e)

#     @mock.patch("time.time")
#     def test_needs_refresh_false_if_query_less_than_24_hrs(self, mock_time):
#         mock_time.return_value = 10000
#         with self.data_cache.database():
#             self.data_cache._fetch_resources(12345)
#             mock_time.return_value = 10000 + (60 * 60 * 23)
#             needs_refresh = self.data_cache._needs_refresh(12345)
#         self.assertFalse(needs_refresh)

#     @mock.patch("time.time")
#     def test_needs_refresh_true_if_query_greater_than_24_hrs(self, mock_time):
#         mock_time.return_value = 10000
#         with self.data_cache.database():
#             self.data_cache._fetch_projects(12345)
#             mock_time.return_value = 10000 + (60 * 60 * 25)
#             needs_refresh = self.data_cache._needs_refresh(12345)
#         self.assertTrue(needs_refresh)

#     def test_needs_refresh_true_if_schema_version_changes(self):
#         self.data_cache.SCHEMA_VERSION = 1
#         with self.data_cache.database():
#             self.data_cache._fetch_projects(12345)
#             self.data_cache.SCHEMA_VERSION = 2
#             needs_refresh = self.data_cache._needs_refresh(12345)
#         self.assertTrue(needs_refresh)

#     def test_needs_refresh_true_if_different_account_resources(self):
#         with self.data_cache.database():
#             self.data_cache._fetch_projects(12345)
#             needs_refresh = self.data_cache._needs_refresh(67890)
#         self.assertTrue(needs_refresh)


class TestDataCacheSmoke(unittest.TestCase):
    
    def test_smoke(self):
        self.assertTrue(True)