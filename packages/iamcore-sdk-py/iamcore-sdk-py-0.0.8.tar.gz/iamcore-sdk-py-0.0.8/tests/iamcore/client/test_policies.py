import unittest
import pytest
from iamcore.irn import IRN

from iamcore.client.auth import get_token_with_password, TokenResponse
from iamcore.client.tenant import search_tenant, create_tenant
from iamcore.client.conf import SYSTEM_BACKEND_CLIENT_ID
from iamcore.client.policy import search_policy, CreatePolicyRequest
from tests.conf import IAMCORE_ROOT_USER, IAMCORE_ROOT_PASSWORD


@pytest.fixture(scope="class")
def root_token(request):
    request.cls.root = get_token_with_password("root", SYSTEM_BACKEND_CLIENT_ID,
                                               IAMCORE_ROOT_USER, IAMCORE_ROOT_PASSWORD)


@pytest.fixture(scope="class")
def test_tenant(request):
    request.cls.tenant_name = "iamcore-py-test-policy-tenant"
    request.cls.tenant_display_name = "iamcore_ Python Sdk test policy tenant"
    request.cls.policy_name = "allow-all-iamcore-py-test-policy-CrudPoliciesTestCase"
    request.cls.policy_name_account = request.cls.policy_name + "-account-lvl"
    request.cls.policy_name_tenant = request.cls.policy_name + "-tenant-lvl"
    request.cls.policy_description = "Allow all for iamcore-py-test-policy-tenant tenant"


@pytest.mark.usefixtures("root_token")
@pytest.mark.usefixtures("test_tenant")
class CrudPoliciesTestCase(unittest.TestCase):
    root: TokenResponse
    tenant_name: str
    tenant_display_name: str
    policy_name: str
    policy_name_account: str
    policy_name_tenant: str
    policy_description: str

    def test_00_cleanup_ok(self):
        policies = search_policy(self.root.access_headers, name=self.policy_name).data
        if policies:
            self.assertEqual(len(policies), 0)
            for policy in policies:
                self.assertEqual(policy.name, self.policy_name)
                self.assertTrue(policy.id)
                self.assertTrue(policy.irn)
                self.assertTrue(policy.description)
                policy.delete(self.root.access_headers)
        policies = search_policy(self.root.access_headers, name=self.policy_name)
        self.assertEqual(len(policies.data), 0)

    def test_10_account_policy_ok(self):
        tenants = search_tenant(self.root.access_headers, name=self.tenant_name).data
        tenant = tenants[0] if len(tenants) > 0 else \
            create_tenant(self.root.access_headers, name=self.tenant_name, display_name=self.tenant_display_name)

        policy_req = CreatePolicyRequest(self.policy_name_account, 'account', self.policy_description)
        account = IRN.of(tenant.irn).account_id
        policy_req \
            .with_statement('allow', self.policy_description, [f"irn:{account}:unittest:{tenant.tenant_id}:*"], ['*']) \
            .create(self.root.access_headers)

        policies = search_policy(self.root.access_headers, name=self.policy_name_account).data
        if policies:
            self.assertEqual(len(policies), 1)
            created_policy = policies[0]

            self.assertEqual(created_policy.name, self.policy_name_account)
            self.assertEqual(created_policy.description, self.policy_description)
            self.assertTrue(created_policy.id)
            self.assertTrue(created_policy.irn)
            # assert that we create an account policy
            self.assertEqual(IRN.of(created_policy.irn).tenant_id,'')
            self.assertTrue(created_policy.statements)

    def test_10_tenant_policy_ok(self):
        tenants = search_tenant(self.root.access_headers, name=self.tenant_name).data
        tenant = tenants[0] if len(tenants) > 0 else \
            create_tenant(self.root.access_headers, name=self.tenant_name, display_name=self.tenant_display_name)

        policy_req = CreatePolicyRequest(self.policy_name_tenant, 'tenant', self.policy_description,
                                         tenant_id=tenant.tenant_id)
        account = IRN.of(tenant.irn).account_id
        policy_req \
            .with_statement('allow', self.policy_description, [f"irn:{account}:unittest:{tenant.tenant_id}:*"], ['*']) \
            .create(self.root.access_headers)

        policies = search_policy(self.root.access_headers, name=self.policy_name_tenant).data
        if policies:
            self.assertEqual(len(policies), 1)
            created_policy = policies[0]

            self.assertEqual(created_policy.name, self.policy_name_tenant)
            self.assertEqual(created_policy.description, self.policy_description)
            self.assertTrue(created_policy.id)
            self.assertTrue(created_policy.irn)
            # assert that we create an account policy
            self.assertEqual(IRN.of(created_policy.irn).tenant_id, tenant.tenant_id)
            self.assertTrue(created_policy.statements)

    def test_90_cleanup_ok(self):
        policies = search_policy(self.root.access_headers, name=self.policy_name).data
        if policies:
            self.assertEqual(len(policies), 2)
            for policy in policies:
                self.assertIn(policy.name, (self.policy_name_tenant, self.policy_name_account))
                self.assertTrue(policy.id)
                self.assertTrue(policy.irn)
                self.assertTrue(policy.description)
                policy.delete(self.root.access_headers)
        policies = search_policy(self.root.access_headers, name=self.policy_name).data
        self.assertEqual(len(policies), 0)
