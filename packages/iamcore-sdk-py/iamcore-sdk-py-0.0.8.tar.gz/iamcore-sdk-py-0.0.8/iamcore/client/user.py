from typing import List, Generator, Dict
from uuid import UUID

import requests
from iamcore.irn import IRN
from requests import Response

from iamcore.client.common import to_snake_case, SortOrder, to_dict, generic_search_all, IamEntitiesResponse, \
    IamEntityResponse
from iamcore.client.conf import IAMCORE_URL
from iamcore.client.exceptions import IAMUserException, IAMUnauthorizedException, unwrap_patch, IAMException
from .exceptions import err_chain, unwrap_post, unwrap_put, unwrap_delete, \
    unwrap_get


class User(object):
    id: str
    irn: IRN
    created: str
    updated: str
    tenant_id: str
    auth_id: UUID
    email: str
    enabled: str
    first_name: str
    last_name: str
    username: str
    path: str

    @staticmethod
    def of(item):
        if isinstance(item, User):
            return item
        elif isinstance(item, dict):
            return User(**item)
        raise IAMUserException(f"Unexpected response format")

    def __init__(self, irn: str, **kwargs):
        self.irn = IRN.from_irn_str(irn)
        for k, v in kwargs.items():
            attr = to_snake_case(k)
            setattr(self, attr, v)

    def delete(self, auth_headers: dict[str, str]) -> None:
        delete_user(auth_headers, self.id)

    def to_dict(self):
        return to_dict(self)


class CreateUser(object):
    tenant_id: str
    email: str
    enabled: bool
    first_name: str
    last_name: str
    username: str
    password: str
    confirm_password: str
    path: str

    def __init__(self, tenant_id: str = None, email: str = None, enabled: bool = True, first_name: str = None,
                 last_name: str = None, username: str = None, path: str = None,
                 password: str = None, confirm_password: str = None):
        self.tenant_id = tenant_id
        self.email = email
        self.enabled = enabled
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password = password
        self.confirm_password = confirm_password
        self.path = path

    def create(self, auth_headers: dict[str, str]) -> User:
        return create_user(auth_headers, **to_dict(self))


@err_chain(IAMUserException)
def create_user(auth_headers: dict[str, str],
                payload: Dict[str, str] = None,
                tenant_id: str = None,
                enabled: bool = None,
                first_name: str = None, last_name: str = None,
                email: str = None, username: str = None,
                password: str = None, confirm_password: str = None,
                path: str = None
                ) -> User:
    url = IAMCORE_URL + "/api/v1/users"
    if not payload:
        payload = {
            "tenantId": tenant_id,
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "enabled": enabled,
            "username": username,
            "password": password,
            "confirmPassword": confirm_password,
            "path": path
        }
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    response: Response = requests.request("POST", url, json=payload, headers=headers)
    return IamEntityResponse(User, **unwrap_post(response)).data


@err_chain(IAMUserException)
def get_user_me(auth_headers: dict[str, str]) -> User:
    url = IAMCORE_URL + "/api/v1/users/me"
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    response: Response = requests.request("GET", url, data="", headers=headers)
    return IamEntityResponse(User, **unwrap_get(response)).data


@err_chain(IAMUserException)
def get_irn(auth_headers: dict[str, str]) -> IRN:
    url = IAMCORE_URL + "/api/v1/users/me/irn"
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    response: Response = requests.request("GET", url, data="", headers=headers)
    irn_str = IamEntityResponse(str, **unwrap_get(response)).data
    return IRN.of(irn_str)


@err_chain(IAMUserException)
def update_user(auth_headers: dict[str, str],
                user_id: str,
                payload: Dict[str, str] = None,
                enabled: bool = None,
                first_name: str = None, last_name: str = None,
                email: str = None,
                ) -> None:
    if not auth_headers:
        raise IAMUnauthorizedException(f"Missing authorization headers")
    if not user_id:
        raise IAMUserException(f"Missing user_id")
    url = IAMCORE_URL + "/api/v1/users/" + IRN.of(user_id).to_base64()
    if not payload:
        payload = {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "enabled": enabled,
        }
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    response: Response = requests.request("PATCH", url, json=payload, headers=headers)
    return unwrap_patch(response)


@err_chain(IAMUserException)
def delete_user(auth_headers: dict[str, str], user_id: str) -> None:
    if not auth_headers:
        raise IAMUnauthorizedException(f"Missing authorization headers")
    if not user_id:
        raise IAMUserException(f"Missing user_id")

    url = IAMCORE_URL + "/api/v1/users/" + IRN.of(user_id).to_base64()
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    response: Response = requests.request("DELETE", url, data="", headers=headers)
    return unwrap_delete(response)


@err_chain(IAMUserException)
def user_attach_policies(auth_headers: dict[str, str], user_id: str, policies_ids: List[str]):
    if not auth_headers:
        raise IAMUnauthorizedException(f"Missing authorization headers")
    if not user_id:
        raise IAMUserException(f"Missing user_id")
    if not policies_ids or not isinstance(policies_ids, list):
        raise IAMUserException(f"Missing policies_ids or it's not a list")

    url = IAMCORE_URL + "/api/v1/users/" + user_id + "/policies/attach"
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    payload = {
        "policyIDs": policies_ids
    }

    response = requests.request("PUT", url, json=payload, headers=headers)
    return unwrap_put(response)


@err_chain(IAMUserException)
def user_add_groups(auth_headers: dict[str, str], user_id: str, group_ids: List[str]):
    if not auth_headers:
        raise IAMUnauthorizedException(f"Missing authorization headers")
    if not user_id:
        raise IAMUserException(f"Missing user_id")
    if not group_ids or not isinstance(group_ids, list):
        raise IAMUserException(f"Missing policies_ids or it's not a list")

    url = IAMCORE_URL + "/api/v1/users/" + user_id + "/groups/add"
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    payload = {
        "groupIDs": group_ids
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    raise unwrap_put(response)


@err_chain(IAMUserException)
def search_users(
        auth_headers: dict[str, str],
        email: str = None,
        path: str = None,
        first_name: str = None,
        last_name: str = None,
        username: str = None,
        tenant_id: str = None,
        search: str = None,
        page: int = None,
        page_size: int = None,
        sort: str = None,
        sort_order: SortOrder = None
) -> IamEntitiesResponse[User]:
    url = IAMCORE_URL + "/api/v1/users"

    querystring = {
        "email": email,
        "path": path,
        "firstName": first_name,
        "lastName": last_name,
        "username": username,
        "tenantID": tenant_id,
        "search": search,
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

    response = requests.request("GET", url, data="", headers=auth_headers, params=querystring)
    return IamEntitiesResponse(User, **unwrap_get(response))


@err_chain(IAMException)
def search_all_users(auth_headers: dict[str, str], *vargs, **kwargs) -> Generator[User, None, None]:
    return generic_search_all(auth_headers, search_users, *vargs, **kwargs)
