from typing import Generator, List

import requests
from iamcore.irn import IRN
from requests import Response

from iamcore.client.common import to_snake_case, to_dict, SortOrder, generic_search_all, IamEntityResponse, \
    IamEntitiesResponse
from iamcore.client.conf import IAMCORE_URL
from iamcore.client.exceptions import err_chain, IAMException, unwrap_post, unwrap_get, IAMUnauthorizedException, \
    unwrap_put


class IAMEntityBase(object):
    def __int__(self, *vargs, **kwargs):
        pass

    @staticmethod
    def of(item):
        pass


class Application(IAMEntityBase):
    id: str
    irn: IRN
    name: str
    display_name: str
    created: str
    updated: str

    def __init__(self, irn: str, **kwargs):
        self.irn = IRN.from_irn_str(irn)
        for k, v in kwargs.items():
            attr = to_snake_case(k)
            setattr(self, attr, v)

    @staticmethod
    def of(item):
        if isinstance(item, Application):
            return item
        elif isinstance(item, dict):
            return Application(**item)
        raise IAMException(f"Unexpected response format")

    def to_dict(self):
        return to_dict(self)


@err_chain(IAMException)
def create_application(auth_headers: dict[str, str], payload: dict[str, str] = None,
                       name: str = None, display_name: str = None) -> Application:
    url = IAMCORE_URL + "/api/v1/applications"
    if not payload:
        payload = {
            "name": name,
            "displayName": display_name
        }
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    response: Response = requests.request("POST", url, json=payload, headers=headers)
    return IamEntityResponse(Application, **unwrap_post(response)).data


@err_chain(IAMException)
def get_application(headers: dict[str, str], irn: str) -> Application:
    url = IAMCORE_URL + "/api/v1/applications/" + str(irn)
    response: Response = requests.request("GET", url, data="", headers=headers)
    return IamEntityResponse(Application, **unwrap_get(response)).data


@err_chain(IAMException)
def application_attach_policies(auth_headers: dict[str, str], application_id: str, policies_ids: List[str]):
    if not auth_headers:
        raise IAMUnauthorizedException(f"Missing authorization headers")
    if not application_id:
        raise IAMException(f"Missing user_id")
    if not policies_ids or not isinstance(policies_ids, list):
        raise IAMException(f"Missing policies_ids or it's not a list")

    url = IAMCORE_URL + "/api/v1/applications/" + application_id + "/policies/attach"
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    payload = {
        "policyIDs": policies_ids
    }

    response = requests.request("PUT", url, json=payload, headers=headers)
    return unwrap_put(response)


@err_chain(IAMException)
def search_application(
        headers: dict[str, str],
        irn: str = None,
        name: str = None,
        display_name: str = None,
        page: int = None,
        page_size: int = None,
        sort: str = None,
        sort_order: SortOrder = None
) -> IamEntitiesResponse[Application]:
    url = IAMCORE_URL + "/api/v1/applications"

    querystring = {
        "irn": str(irn) if irn else None,
        "name": name,
        "displayName": display_name,
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
    return IamEntitiesResponse(Application, **unwrap_get(response))


@err_chain(IAMException)
def search_all_applications(auth_headers: dict[str, str], *vargs, **kwargs) -> Generator[Application, None, None]:
    return generic_search_all(auth_headers, search_application, *vargs, **kwargs)
