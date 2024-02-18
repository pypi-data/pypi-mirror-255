from typing import List, Generator

import requests
from iamcore.irn import IRN
from requests import Response

from iamcore.client.common import to_snake_case, to_dict, SortOrder, generic_search_all, IamEntityResponse, \
    IamEntitiesResponse
from iamcore.client.conf import IAMCORE_URL
from iamcore.client.exceptions import err_chain, IAMException, unwrap_post, unwrap_get


class ApplicationResourceType(object):
    id: str
    irn: IRN
    type: str
    description: str
    action_prefix: str
    operations: List[str]
    created: str
    updated: str

    def __init__(self, irn: str, **kwargs):
        self.irn = IRN.from_irn_str(irn)
        for k, v in kwargs.items():
            attr = to_snake_case(k)
            setattr(self, attr, v)

    @staticmethod
    def of(item):
        if isinstance(item, ApplicationResourceType):
            return item
        elif isinstance(item, dict):
            return ApplicationResourceType(**item)
        raise IAMException(f"Unexpected response format")

    def to_dict(self):
        return to_dict(self)


@err_chain(IAMException)
def create_resource_type(
        auth_headers: dict[str, str],
        application_irn: IRN,
        payload: dict[str, str] = None,
        type: str = None,
        description: str = None,
        action_prefix: str = None,
        operations: List[str] = None
) -> ApplicationResourceType:
    url = IAMCORE_URL + "/api/v1/applications/" + IRN.of(application_irn).to_base64() + "/resource-types"
    if not payload:
        payload = {
            "type": type,
            "description": description,
            "actionPrefix": action_prefix,
            "operations": operations,
        }
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    response: Response = requests.request("POST", url, json=payload, headers=headers)
    return IamEntityResponse(ApplicationResourceType, **unwrap_post(response)).data


@err_chain(IAMException)
def get_resource_type(
        auth_headers: dict[str, str],
        application_irn: IRN,
        irn: IRN,
) -> ApplicationResourceType:
    url = (IAMCORE_URL + "/api/v1/applications/" + IRN.of(application_irn).to_base64() +
           "/resource-types/" + IRN.of(irn).to_base64())
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    response: Response = requests.request("GET", url, headers=headers)
    return IamEntityResponse(ApplicationResourceType, **unwrap_get(response)).data


@err_chain(IAMException)
def search_application_resource_types(
        headers: dict[str, str],
        application_irn: IRN,
        page: int = None,
        page_size: int = None,
        sort: str = None,
        sort_order: SortOrder = None
) -> IamEntitiesResponse[ApplicationResourceType]:
    url = IAMCORE_URL + "/api/v1/applications/" + IRN.of(application_irn).to_base64() + "/resource-types"

    querystring = {
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
    return IamEntitiesResponse(ApplicationResourceType, **unwrap_get(response))


@err_chain(IAMException)
def search_all_application_resource_types(
        auth_headers: dict[str, str], *vargs, **kwargs
) -> Generator[ApplicationResourceType, None, None]:
    return generic_search_all(auth_headers, search_application_resource_types, *vargs, **kwargs)
