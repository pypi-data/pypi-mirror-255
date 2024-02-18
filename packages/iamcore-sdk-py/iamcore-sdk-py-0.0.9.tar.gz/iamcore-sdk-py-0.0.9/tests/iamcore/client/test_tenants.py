import unittest
import pytest
from iamcore.irn import IRN

from iamcore.client.auth import get_token_with_password, TokenResponse
from iamcore.client.tenant import search_tenant, create_tenant, get_issuer
from iamcore.client.config import config

from tests.conf import IAMCORE_ROOT_USER, IAMCORE_ROOT_PASSWORD


@pytest.fixture(scope="class")
def root_token(request):
    request.cls.root = get_token_with_password("root", config.SYSTEM_BACKEND_CLIENT_ID,
                                               IAMCORE_ROOT_USER, IAMCORE_ROOT_PASSWORD)


@pytest.fixture(scope="class")
def test_tenant(request):
    request.cls.tenant_name = "iamcore-py-test-tenant"
    request.cls.tenant_display_name = "iamcore_ Python Sdk test tenant"
    request.cls.login_theme = 'kaa'


@pytest.mark.usefixtures("root_token")
@pytest.mark.usefixtures("test_tenant")
class CrudTenantsTestCase(unittest.TestCase):
    root: TokenResponse
    tenant_name: str
    tenant_display_name: str
    login_theme: str

    def test_00_cleanup_ok(self):
        tenants = search_tenant(self.root.access_headers, name=self.tenant_name).data
        if tenants:
            self.assertLessEqual(len(tenants), 1)
            for tenant in tenants:
                self.assertEqual(tenant.name, self.tenant_name)
                self.assertTrue(tenant.display_name)
                self.assertTrue(tenant.irn)
                self.assertTrue(tenant.tenant_id)
                self.assertTrue(tenant.resource_id)
                self.assertTrue(tenant.created)
                self.assertTrue(tenant.updated)
                tenant.delete(self.root.access_headers)
        tenants = search_tenant(self.root.access_headers, name=self.tenant_name).data
        self.assertFalse(tenants)

    def test_10_crud_ok(self):
        name = self.tenant_name + '_10'
        tenant_display_name = self.tenant_display_name + '_10'
        tenant = create_tenant(self.root.access_headers, name=name, display_name=tenant_display_name,
                               login_theme=self.login_theme)

        self.assertEqual(tenant.name, name)
        self.assertEqual(tenant.display_name, tenant_display_name)
        self.assertTrue(tenant.irn)
        self.assertTrue(tenant.tenant_id)
        self.assertTrue(tenant.resource_id)
        self.assertTrue(tenant.created)
        self.assertTrue(tenant.updated)
        self.assertEqual(self.login_theme, tenant.login_theme)

    def test_12_default_login_theme_ok(self):
        name = self.tenant_name + '_12'
        tenant_display_name = self.tenant_display_name + '_12'
        tenant = create_tenant(self.root.access_headers, name=name, display_name=tenant_display_name)

        self.assertEqual(tenant.name, name)
        self.assertEqual(tenant.display_name, tenant_display_name)
        self.assertTrue(tenant.irn)
        self.assertTrue(tenant.tenant_id)
        self.assertTrue(tenant.resource_id)
        self.assertTrue(tenant.created)
        self.assertTrue(tenant.updated)
        self.assertEqual('iamcore', tenant.login_theme)

    def test_14_update_ok(self):
        name = self.tenant_name + '_12'
        tenant_display_name = self.tenant_display_name + '_12'
        tenants = search_tenant(self.root.access_headers, name=name).data
        self.assertEqual(len(tenants), 1)
        tenant = tenants[0]

        tenant.display_name = tenant_display_name + " updated"

        tenant.update(self.root.access_headers)
        self.assertEqual(tenant.name, name)
        self.assertEqual(tenant.display_name, tenant_display_name + " updated")
        self.assertTrue(tenant.irn)
        self.assertTrue(tenant.tenant_id)
        self.assertTrue(tenant.resource_id)
        self.assertTrue(tenant.created)
        self.assertTrue(tenant.updated)

    def test_20_issuer_ok(self):
        tenants = search_tenant(self.root.access_headers, name=self.tenant_name+'_10').data
        self.assertLessEqual(len(tenants), 1)
        tenant = tenants[0]
        account = IRN.of(tenant.irn).account_id
        issuer = get_issuer(self.root.access_headers, account, tenant.tenant_id)
        self.assertTrue(issuer)
        self.assertEqual(str(issuer.irn), str(IRN.of(f'irn:{account}:iamcore:{tenant.tenant_id}::issuer/iamcore')))
        self.assertEqual(issuer.url, f"{config.IAMCORE_ISSUER_URL.strip()}/realms/{tenant.tenant_id}")
        self.assertEqual(issuer.login_url,
                         f"{config.IAMCORE_ISSUER_URL.strip()}/realms/{tenant.tenant_id}/protocol/openid-connect/auth")
        self.assertTrue(issuer.client_id)

    def test_20_search_ok(self):
        name = self.tenant_name + '_10'
        tenant_display_name = self.tenant_display_name + '_10'
        tenants = search_tenant(self.root.access_headers, name=name).data
        self.assertEqual(len(tenants), 1)
        tenant = tenants[0]

        search_plan = [
            ('name', tenant.name),
            ('display_name', tenant.display_name),
            ('irn', tenant.irn),
            ('tenant_id', tenant.tenant_id)
        ]

        for param, value in search_plan:
            tenants = search_tenant(self.root.access_headers, **{param: value}).data
            self.assertEqual(len(tenants), 1)
            self.assertTrue(tenants[0].name.startswith(tenant.name))
            self.assertEqual(tenants[0].display_name, tenant.display_name)
            self.assertTrue(tenants[0].irn, tenant.irn)
            self.assertTrue(tenants[0].tenant_id, tenant.tenant_id)
            self.assertTrue(tenants[0].resource_id, tenant.resource_id)
            self.assertTrue(tenants[0].created, tenant.created)
            self.assertTrue(tenants[0].updated, tenant.updated)

    def test_90_cleanup_ok(self):
        tenants = search_tenant(self.root.access_headers, name=self.tenant_name).data
        if tenants:
            self.assertLessEqual(len(tenants), 2)
            for tenant in tenants:
                self.assertTrue(tenant.name.startswith(self.tenant_name))
                self.assertTrue(tenant.display_name)
                self.assertTrue(tenant.irn)
                self.assertTrue(tenant.tenant_id)
                self.assertTrue(tenant.resource_id)
                self.assertTrue(tenant.created)
                self.assertTrue(tenant.updated)
                tenant.delete(self.root.access_headers)
        tenants = search_tenant(self.root.access_headers, name=self.tenant_name).data
        self.assertFalse(tenants)
