from typing import Generator

import requests
from iamcore.irn import IRN
from requests import Response

from iamcore.client.conf import IAMCORE_URL
from .common import SortOrder, to_snake_case, to_dict, generic_search_all, IamEntityResponse, IamEntitiesResponse
from .exceptions import IAMTenantException, err_chain, unwrap_post, unwrap_put, unwrap_delete, \
    unwrap_get, IAMException


class Tenant(object):
    resource_id: str
    irn: IRN
    tenant_id: str
    name: str
    display_name: str
    login_theme: str
    created: str
    updated: str

    def __init__(self, irn: str, **kwargs):
        self.irn = IRN.from_irn_str(irn)
        for k, v in kwargs.items():
            attr = to_snake_case(k)
            setattr(self, attr, v)

    @staticmethod
    def of(item):
        if isinstance(item, Tenant):
            return item
        elif isinstance(item, dict):
            return Tenant(**item)
        raise IAMTenantException(f"Unexpected response format")

    def to_dict(self):
        return to_dict(self)

    def update(self, auth_headers: dict[str, str]) -> None:
        return update_tenant(auth_headers, self.resource_id, self.display_name)

    def delete(self, auth_headers: dict[str, str]):
        return delete_tenant(auth_headers, self.resource_id)


class TenantIssuer(object):
    id: str
    irn: IRN
    name: str
    type: str
    url: str
    client_id: str
    login_url: str

    def __init__(self, irn: str, **kwargs):
        self.irn = IRN.from_irn_str(irn)
        for k, v in kwargs.items():
            attr = to_snake_case(k)
            setattr(self, attr, v)

    @staticmethod
    def of(item):
        if isinstance(item, TenantIssuer):
            return item
        elif isinstance(item, dict):
            return TenantIssuer(**item)
        raise IAMTenantException(f"Unexpected response format")

    def to_dict(self):
        return to_dict(self)

    def update(self, auth_headers: dict[str, str]) -> None:
        return update_tenant(auth_headers, self.resource_id, self.display_name)

    def delete(self, auth_headers: dict[str, str]):
        return delete_tenant(auth_headers, self.resource_id)


@err_chain(IAMTenantException)
def create_tenant(auth_headers: dict[str, str], payload: dict[str, str] = None,
                  name: str = None, display_name: str = None, login_theme: str = None) -> Tenant:
    url = IAMCORE_URL + "/api/v1/tenants/issuer-types/iamcore"
    if not payload:
        payload = {
            "name": name,
            "displayName": display_name,
            "loginTheme": login_theme,
        }
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    response: Response = requests.request("POST", url, json=payload, headers=headers)
    return IamEntityResponse(Tenant, **unwrap_post(response)).data


@err_chain(IAMTenantException)
def update_tenant(auth_headers: dict[str, str], resource_id: str, display_name: str) -> None:
    if not auth_headers:
        raise IAMTenantException(f"Missing authorization headers")
    if not resource_id or not display_name:
        raise IAMTenantException(f"Missing resource_id or display_name")

    url = IAMCORE_URL + "/api/v1/tenants/" + IRN.of(resource_id).to_base64()
    payload = {
        "displayName": display_name
    }
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    response: Response = requests.request("PUT", url, json=payload, headers=headers)
    return unwrap_put(response)


@err_chain(IAMTenantException)
def delete_tenant(auth_headers: dict[str, str], resource_id: str) -> None:
    if not auth_headers:
        raise IAMTenantException(f"Missing authorization headers")
    if not resource_id:
        raise IAMTenantException(f"Missing resource_id")

    url = IAMCORE_URL + "/api/v1/tenants/" + IRN.of(resource_id).to_base64()
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    response: Response = requests.request("DELETE", url, data="", headers=headers)
    return unwrap_delete(response)


@err_chain(IAMTenantException)
def get_issuer(
        headers: dict[str, str],
        account: str = None,
        tenant_id: str = None,
) -> TenantIssuer:
    url = IAMCORE_URL + "/api/v1/tenants/issuers"

    querystring = {
        "account": account,
        "tenant": tenant_id,
    }

    response: Response = requests.request("GET", url, data="", headers=headers, params=querystring)
    return IamEntitiesResponse(TenantIssuer, **unwrap_get(response)).data.pop()


@err_chain(IAMTenantException)
def search_tenant(
        headers: dict[str, str],
        irn: str = None,
        tenant_id: str = None,
        name: str = None,
        display_name: str = None,
        issuer_type: str = None,
        page: int = None,
        page_size: int = None,
        sort: str = None,
        sort_order: SortOrder = None
) -> IamEntitiesResponse[Tenant]:
    url = IAMCORE_URL + "/api/v1/tenants"

    querystring = {
        "irn": str(irn) if irn else None,
        "name": name,
        "displayName": display_name,
        "tenantID": tenant_id,
        "issuerType": issuer_type,
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

    response: Response = requests.request("GET", url, data="", headers=headers, params=querystring)
    return IamEntitiesResponse(Tenant, **unwrap_get(response))


@err_chain(IAMException)
def search_all_tenants(auth_headers: dict[str, str], *vargs, **kwargs) -> Generator[Tenant, None, None]:
    return generic_search_all(auth_headers, search_tenant, *vargs, **kwargs)
