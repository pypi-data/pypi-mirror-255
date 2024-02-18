""" test data

   isort:skip_file
"""

import unittest

try:
    from unittest import mock
except ImportError:
    import mock

from ciocore import data


from project_fixtures import PROJECTS
from package_fixtures import SOFTWARE_DATA
from instance_type_fixtures import LIN_INSTANCE_TYPES, ALL_INSTANCE_TYPES

class TestDataAllInstanceTypes(unittest.TestCase):
    def setUp(self):
        self.default_cache = {
            "projects": PROJECTS,
            "instance_types": ALL_INSTANCE_TYPES,
            "packages": SOFTWARE_DATA,
        }

        # self.get_data_patcher = mock.patch.object(DataCache, "get_data", return_value=self.default_cache)

        # self.account_id_patcher = mock.patch(
        #     "ciocore.data.get_account_id", return_value="1234"
        # )

        # self.mock_get_data = self.get_data_patcher.start()
        # self.mock_account_id = self.account_id_patcher.start()

        data.__data__ = {}
        data.__products__ = None

    def tearDown(self):
        # self.get_data_patcher.stop()
        # self.account_id_patcher.stop()
        pass

    # def override_default_cache(self, **kwargs):
    #     return_val = {}
    #     return_val.update(self.default_cache)
    #     return_val.update(kwargs)
        # self.mock_get_data.return_value = return_val

    # def test_smoke(self):
    #     self.assertEqual(1, 1)

    # def test_init_empty_projects_global(self):
    #     data.init()
    #     self.assertEqual(data.products(), [])

    # def test_init_stores_all_args(self):
    #     data.init("a", "b", "c")
    #     self.assertEqual(data.products(), ["a", "b", "c"])

    # def test_data_raises_if_not_initialized(self):
    #     with self.assertRaises(ValueError):
    #         data.data()

    # def test_valid(self):
    #     self.assertEqual(data.valid(), False)
    #     data.init()
    #     data.data()
    #     self.assertEqual(data.valid(), True)

    # def test_clear(self):
    #     data.init()
    #     data.data()
    #     self.assertEqual(data.valid(), True)
    #     data.clear()
    #     self.assertEqual(data.valid(), False)

    # def test_does_not_refresh_if_not_force(self):
    #     data.init()
    #     p1 = data.data()["projects"]
    #     self.assertEqual(len(p1), 4)
    #     # merge the default cache with a new projects list containing only two projects
    #     # self.override_default_cache(projects=["a", "b"])
    #     p2 = data.data()["projects"]
    #     self.assertEqual(p2, p1)

    # def test_does_refresh_if_force_all(self):
    #     data.init()
    #     p1 = data.data()["projects"]
    #     self.assertEqual(len(p1), 4)
    #     # self.override_default_cache(projects=["a", "b"])
    #     p2 = data.data(force=True)["projects"]
    #     self.assertNotEqual(p2, p1)
    #     self.assertEqual(len(p2), 2)

    # def test_get_data_for_one_product(self):
    #     data.init("c4d")
    #     # inst = data.data()["instance_types"]
    #     sw = data.data()["software"]
    #     self.assertEqual(len(sw.supported_host_names()), 2)

    # def test_several_products(self):
    #     data.init("c4d", "maya")
    #     sw = data.data()["software"]
    #     self.assertEqual(len(sw.supported_host_names()), 5)

    # def test_one_product_can_be_a_plugin(self):
    #     data.init("redshift")
    #     sw = data.data()["software"]
    #     self.assertEqual(len(sw.supported_host_names()), 4)

    # def test_several_products_ignore_plugins(self):
    #     data.init("redshift", "c4d")
    #     sw = data.data()["software"]
    #     self.assertEqual(len(sw.supported_host_names()), 2)

    # def test_linux_only_instance_types(self):
    #     # self.override_default_cache(instance_types=LIN_INSTANCE_TYPES)
    #     data.init()
    #     h = data.data()["instance_types"]
    #     self.assertEqual(len(h.instance_types.keys()), 4)

    # def test_linux_only_packages_when_linux_only_instance_types(self):
    #     # self.override_default_cache(instance_types=LIN_INSTANCE_TYPES)
    #     data.init("c4d")
    #     sw = data.data()["software"]
    #     self.assertEqual(len(sw.supported_host_names()), 1)

    # def test_platforms_method_only_linux(self):
    #     self.override_default_cache(instance_types=LIN_INSTANCE_TYPES)/
    #     data.init("c4d")
    #     data.data()
    #     self.assertEqual({"linux"}, data.platforms())

    # def test_many_products(self):
    #     self.override_default_cache(instance_types=LIN_INSTANCE_TYPES)
    #     data.init("c4d", "maya")
    #     sw = data.data()["software"]
    #     self.assertEqual(len(sw.supported_host_names()), 4)

    # def test_product_keyword_translates_to_single_arg(self):
    #     data.init(product="c4d")
    #     sw = data.data()["software"]
    #     self.assertEqual(len(sw.supported_host_names()), 2)

    # def test_product_keyword_all_translates_to_all_products(self):
    #     data.init(product="all")
    #     sw = data.data()["software"]
    #     self.assertEqual(len(sw.supported_host_names()), 11)

    # def test_data_raises_if_both_products_and_kwarg_given(self):
    #     with self.assertRaises(ValueError):
    #         data.init("maya", product="c4d")

    # def test_data_raises_if_products_and_kwarg_given(self):
    #     with self.assertRaises(ValueError):
    #         data.init("maya", product="c4d")

class TestDataSmoke(unittest.TestCase):
    
    def test_smoke(self):
        self.assertTrue(True)