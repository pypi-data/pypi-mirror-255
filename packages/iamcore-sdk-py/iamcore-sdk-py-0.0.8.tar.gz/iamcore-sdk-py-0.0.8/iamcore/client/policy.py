import logging
from typing import List, Generator

import requests
from iamcore.irn import IRN
from requests import Response

from iamcore.client.conf import IAMCORE_URL
from .common import SortOrder, to_dict, generic_search_all, IamEntitiesResponse, IamEntityResponse
from .exceptions import IAMPolicyException, IAMUnauthorizedException, err_chain, unwrap_post, \
    unwrap_delete, unwrap_get, unwrap_put, IAMException


logger = logging.getLogger(__name__)


class PolicyStatement(object):
    effect: str
    description: str
    resources: List[IRN]
    actions: List[str]

    @staticmethod
    def of(item):
        if isinstance(item, PolicyStatement):
            return item
        elif isinstance(item, dict):
            return PolicyStatement(**item)
        raise IAMPolicyException(f"Unexpected response format")

    def __init__(self, effect: str = None, description: str = None,
                 resources: List[str] = None, actions: List[str] = None):
        self.effect = effect
        self.description = description
        self.resources = [IRN.of(irn) for irn in resources]
        self.actions = actions


class Policy(object):
    id: str
    irn: IRN
    name: str
    description: str
    type: str
    origin: str
    version: str
    statements: List[PolicyStatement]

    def __init__(self, irn: str, statements: List[dict] = None, **kwargs):
        self.irn = IRN.of(irn)
        if isinstance(statements, List):
            self.statements = [
                PolicyStatement.of(item)
                for item in statements
            ]
        for k, v in kwargs.items():
            setattr(self, k, v)

    @staticmethod
    def of(item):
        if isinstance(item, Policy):
            return item
        elif isinstance(item, dict):
            return Policy(**item)
        raise IAMPolicyException(f"Unexpected response format")

    @err_chain(IAMPolicyException)
    def update(self, auth_headers: dict[str, str]) -> None:
        if not auth_headers:
            raise IAMUnauthorizedException(f"Missing authorization headers")
        if not self.id:
            raise IAMPolicyException(f"Missing resource_id or display_name")

        url = IAMCORE_URL + "/api/v1/policies/" + self.id
        payload = to_dict(self)
        headers = {
            "Content-Type": "application/json",
            **auth_headers
        }
        response: Response = requests.request("PUT", url, json=payload, headers=headers)
        unwrap_put(response)

    def delete(self, auth_headers: dict[str, str]) -> None:
        delete_policy(auth_headers, policy_id=self.id)

    def to_dict(self):
        return to_dict(self)


class CreatePolicyRequest(object):
    name: str
    level: str
    tenant_id: str
    description: str
    statements: List[PolicyStatement]

    def __init__(self, name: str, level: str, description: str, tenant_id: str = None):
        self.name = name
        self.level = level
        self.tenant_id = tenant_id
        self.description = description
        self.statements = []
        if level == 'tenant' and not tenant_id:
            logger.warning("Missing tenant_id for tenant level policy")


    def with_statement(self, effect: str, description: str, resources: List[str], actions: List[str]):
        self.statements.append(PolicyStatement(
            effect=effect, description=description, resources=resources, actions=actions))
        return self

    @err_chain(IAMPolicyException)
    def create(self, auth_headers: dict[str, str]) -> Policy:
        return create_policy(auth_headers, self)

    def to_dict(self):
        return {
            'name': self.name,
            'level': self.level,
            'description': self.description,
            'tenantID': self.tenant_id,
            'statements': to_dict(self.statements),
        }


@err_chain(IAMPolicyException)
def create_policy(auth_headers: dict[str, str], payload: CreatePolicyRequest) -> Policy:
    url = IAMCORE_URL + "/api/v1/policies"
    payload = payload.to_dict()

    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    response: Response = requests.request("POST", url, json=payload, headers=headers)
    return IamEntityResponse(Policy, **unwrap_post(response)).data


@err_chain(IAMPolicyException)
def delete_policy(auth_headers: dict[str, str], policy_id: str) -> None:
    if not auth_headers:
        raise IAMUnauthorizedException(f"Missing authorization headers")
    if not policy_id:
        raise IAMPolicyException(f"Missing resource_id")

    url = IAMCORE_URL + "/api/v1/policies/" + IRN.of(policy_id).to_base64()
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    response: Response = requests.request("DELETE", url, data="", headers=headers)
    unwrap_delete(response)


@err_chain(IAMPolicyException)
def search_policy(
        headers: dict[str, str],
        irn: str = None,
        name: str = None,
        description: str = None,
        page: int = None,
        page_size: int = None,
        sort: str = None,
        sort_order: SortOrder = None
) -> IamEntitiesResponse[Policy]:
    url = IAMCORE_URL + "/api/v1/policies"

    querystring = {
        "irn": irn,
        "name": name,
        "description": description,
        "page": page,
        "pageSize": page_size,
        "sort": sort,
        "sortOrder": sort_order
    }

    querystring = {
        k: v
        for k, v in querystring.items()
        if v
    }

    response = requests.request("GET", url, data="", headers=headers, params=querystring)
    return IamEntitiesResponse(Policy, **unwrap_get(response))


@err_chain(IAMException)
def search_all_policies(auth_headers: dict[str, str], *vargs, **kwargs) -> Generator[Policy, None, None]:
    return generic_search_all(auth_headers, search_policy, *vargs, **kwargs)
