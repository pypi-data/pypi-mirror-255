import unittest

from iamcore.client.application import search_all_applications
from iamcore.client.application_api_key import get_application_api_keys, get_all_applications_api_keys
from iamcore.client.auth import get_token_with_password
from iamcore.client.exceptions import IAMUnauthorizedException, IAMException
from iamcore.client.conf import SYSTEM_BACKEND_CLIENT_ID
from tests.conf import IAMCORE_ROOT_USER, IAMCORE_ROOT_PASSWORD


class GetTokenTestCase(unittest.TestCase):
    def test_token_with_password_ok(self) -> None:
        credentials = get_token_with_password("root", SYSTEM_BACKEND_CLIENT_ID,
                                              IAMCORE_ROOT_USER, IAMCORE_ROOT_PASSWORD)
        self.assertTrue(bool(credentials.access_token))
        self.assertTrue(bool(credentials.refresh_token))
        self.assertTrue(bool(credentials.scope))
        self.assertTrue(bool(credentials.token_type))
        self.assertTrue(bool(credentials.session_state))

    def test_token_with_password_fail(self) -> None:
        with self.assertRaises(IAMUnauthorizedException) as context:
            get_token_with_password("root", SYSTEM_BACKEND_CLIENT_ID, IAMCORE_ROOT_USER, 'nopassword')
        self.assertTrue('Unauthorized:' in context.exception.msg)

    def test_get_api_key(self) -> None:
        application_name = 'kaa'

        token = get_token_with_password("root", SYSTEM_BACKEND_CLIENT_ID, IAMCORE_ROOT_USER, IAMCORE_ROOT_PASSWORD)
        applications = [
            a for a in search_all_applications(token.access_headers, name=application_name)
            if application_name == a.name
        ]
        self.assertGreaterEqual(len(applications), 1)
        for a in applications:
            api_key = next(get_all_applications_api_keys(token.access_headers, a.irn))
            self.assertIsNotNone(api_key)
            self.assertIsNotNone(api_key.api_key)
            self.assertIsInstance(api_key.api_key, str)
            self.assertTrue(api_key.api_key)
