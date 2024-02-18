import http.client
from typing import List, Generator

import requests
from iamcore.irn import IRN
from requests import Response

from iamcore.client.common import to_snake_case, SortOrder, generic_search_all, IamEntityResponse, IamEntitiesResponse
from iamcore.client.conf import IAMCORE_URL
from iamcore.client.exceptions import IAMUnauthorizedException, err_chain, IAMGroupException, IAMException, unwrap_post, \
    unwrap_delete, unwrap_put, unwrap_get


class Group(object):
    id: str
    irn: IRN
    tenant_id: str
    name: str
    display_name: str
    path: str
    created: str
    updated: str

    @staticmethod
    def of(item):
        if isinstance(item, Group):
            return item
        elif isinstance(item, dict):
            return Group(**item)
        raise IAMGroupException(f"Unexpected response format")

    def __init__(self, irn: str, **kwargs):
        self._irn = IRN.from_irn_str(irn)
        for k, v in kwargs.items():
            attr = to_snake_case(k)
            setattr(self, attr, v)


@err_chain(IAMGroupException)
def create_group(auth_headers: dict[str, str], payload: dict[str, object] = None,
                 name: str = None, display_name: str = None,
                 tenant_id: str = None, parent_id: str = None) -> Group:
    url = IAMCORE_URL + "/api/v1/groups"
    if not payload:
        payload = {
            "name": name,
            "displayName": display_name,
            "parentID": parent_id,
            "tenantID": tenant_id
        }
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    response: Response = requests.request("POST", url, json=payload, headers=headers)
    return IamEntityResponse(Group, **unwrap_post(response)).data


@err_chain(IAMGroupException)
def delete_group(auth_headers: dict[str, str], group_id: str) -> None:
    if not auth_headers:
        raise IAMUnauthorizedException(f"Missing authorization headers")
    if not group_id:
        raise IAMGroupException(f"Missing group_id")

    url = IAMCORE_URL + "/api/v1/groups/" + IRN.of(group_id).to_base64()
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    response: Response = requests.request("DELETE", url, data="", headers=headers)
    unwrap_delete(response)


@err_chain(IAMGroupException)
def group_attach_policies(auth_headers: dict[str, str], group_id: str, policies_ids: List[str]):
    if not auth_headers:
        raise IAMUnauthorizedException(f"Missing authorization headers")
    if not group_id:
        raise IAMGroupException(f"Missing group_id")
    if not policies_ids or not isinstance(policies_ids, list):
        raise IAMGroupException(f"Missing policies_ids or it's not a list")

    url = IAMCORE_URL + "/api/v1/groups/" + group_id + "/policies/attach"
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    payload = {
        "policyIDs": policies_ids
    }

    response = requests.request("PUT", url, json=payload, headers=headers)
    unwrap_put(response)


@err_chain(IAMGroupException)
def group_add_members(auth_headers: dict[str, str], group_id: str, members_ids: List[str]):
    if not auth_headers:
        raise IAMUnauthorizedException(f"Missing authorization headers")
    if not group_id:
        raise IAMGroupException(f"Missing group_id")
    if not members_ids or not isinstance(members_ids, list):
        raise IAMGroupException(f"Missing policies_ids or it's not a list")

    url = IAMCORE_URL + "/api/v1/groups/" + group_id + "/members/add"
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    payload = {
        "userIDs": members_ids
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    unwrap_put(response)


@err_chain(IAMGroupException)
def search_group(
        headers: dict[str, str],
        irn: IRN = None,
        path: str = None,
        name: str = None,
        display_name: str = None,
        tenant_id: str = None,
        page: int = None,
        page_size: int = None,
        sort: str = None,
        sort_order: SortOrder = None
) -> IamEntitiesResponse[Group]:
    url = IAMCORE_URL + "/api/v1/groups"

    querystring = {
        "irn": str(irn) if irn else None,
        "path": path,
        "name": name,
        "displayName": display_name,
        "tenantID": tenant_id,
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
    return IamEntitiesResponse(Group, **unwrap_get(response))


@err_chain(IAMException)
def search_all_groups(auth_headers: dict[str, str], *vargs, **kwargs) -> Generator[Group, None, None]:
    return generic_search_all(auth_headers, search_group, *vargs, **kwargs)
