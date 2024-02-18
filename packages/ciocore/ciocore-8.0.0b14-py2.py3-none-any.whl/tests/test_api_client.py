""" test data

   isort:skip_file
"""
import sys
import unittest

try:
    from unittest import mock
except ImportError:
    import mock

from ciocore import api_client


class ApiClientTest(unittest.TestCase):
    @staticmethod
    def path_exists_side_effect(arg):
        if "missing" in arg:
            return False
        else:
            return True

    def setUp(self):
        self.env = {"USERPROFILE": "/users/joebloggs", "HOME": "/users/joebloggs"}

        self.api_key_dict = {"api_key": {"client_id": "123", "private_key": "secret123"}}

        patcher = mock.patch("os.path.exists")
        self.mock_exists = patcher.start()
        self.mock_exists.side_effect = ApiClientTest.path_exists_side_effect
        self.addCleanup(patcher.stop)

    def test_create(self):
        ac = api_client.ApiClient()
        self.assertEqual(ac.__class__.__name__, "ApiClient")

    def test_get_standard_creds_path(self):
        with mock.patch.dict("os.environ", self.env):
            fn = api_client.get_creds_path(api_key=False).replace("\\", "/")
            self.assertEqual(fn, "/users/joebloggs/.config/conductor/credentials")

    def test_get_api_key_creds_path(self):
        with mock.patch.dict("os.environ", self.env):
            fn = api_client.get_creds_path(api_key=True).replace("\\", "/")
            self.assertEqual(fn, "/users/joebloggs/.config/conductor/api_key_credentials")


class TestTruncateMiddle(unittest.TestCase):

    def test_truncation_not_needed(self):
        self.assertEqual(api_client.truncate_middle("short", 10), "short")

    def test_truncation_with_even_max_length(self):
        self.assertEqual(api_client.truncate_middle("1234567890ABCDEF", 8), "1234~DEF")

    def test_truncation_with_odd_max_length(self):
        self.assertEqual(api_client.truncate_middle("1234567890ABCDEF", 9), "1234~CDEF")

    def test_empty_string(self):
        self.assertEqual(api_client.truncate_middle("", 5), "")

    def test_non_string_input(self):
        with self.assertRaises(TypeError):
            api_client.truncate_middle(12345, 5)

class TestRegisterClient(unittest.TestCase):
    USER_AGENT_MAX_PATH_LENGTH = 10  # Example max length for testing

    @classmethod
    def setUpClass(cls):
        cls.original_executable = sys.executable
        sys.executable = '/usr/bin/python3'  # Example path for testing

    @classmethod
    def tearDownClass(cls):
        sys.executable = cls.original_executable

    def test_register_client_with_version(self):
        client_name = 'ApiClient'
        client_version = '1.0'

        with mock.patch('platform.python_version', return_value='3.8.2'), \
             mock.patch('platform.system', return_value='Linux'), \
             mock.patch('platform.release', return_value='5.4.0-42-generic'):
            user_agent = api_client.ApiClient.register_client(client_name, client_version)

        expected_user_agent = (
            f"ApiClient/1.0 (python 3.8.2; Linux 5.4.0-42-generic; "
        )
        self.assertTrue(user_agent.startswith(expected_user_agent))

    def test_register_client_without_version(self):
        client_name = 'ApiClient'

        with mock.patch('platform.python_version', return_value='3.8.2'), \
             mock.patch('platform.system', return_value='Linux'), \
             mock.patch('platform.release', return_value='5.4.0-42-generic'):
            user_agent =  api_client.ApiClient.register_client(client_name)


        expected_user_agent = (
            f"ApiClient/unknown (python 3.8.2; Linux 5.4.0-42-generic; "
        )

        self.assertTrue(user_agent.startswith(expected_user_agent))

