import http.client
from typing import List, Dict, Generator

import requests
from iamcore.irn import IRN
from requests import Response

from iamcore.client.common import to_snake_case, SortOrder, to_dict, generic_search_all, IamEntityResponse, \
    IamEntitiesResponse
from iamcore.client.conf import IAMCORE_URL
from iamcore.client.exceptions import IAMUnauthorizedException, err_chain, IAMResourceException, unwrap_post, \
    unwrap_put, unwrap_delete, unwrap_get, IAMException


class Resource(object):
    id: str
    irn: IRN
    name: str
    display_name: str
    description: str
    path: str
    tenant_id: str
    application: str
    resourceType: str
    enabled: bool
    metadata: Dict[str, str]
    created: str
    updated: str

    @staticmethod
    def of(item):
        if isinstance(item, Resource):
            return item
        elif isinstance(item, dict):
            return Resource(**item)
        raise IAMResourceException(f"Unexpected response format")

    def __init__(self, irn: str, **kwargs):
        self._irn = IRN.from_irn_str(irn)
        for k, v in kwargs.items():
            attr = to_snake_case(k)
            setattr(self, attr, v)

    def delete(self, auth_headers: Dict[str, str]):
        delete_resource(auth_headers, self.id)

    def update(self, auth_headers: Dict[str, str]):
        update_resource(
            auth_headers,
            resource_id=self.id,
            display_name=self.display_name,
            enabled=self.enabled,
            description=self.description,
            metadata=self.metadata
        )

    def to_dict(self):
        return to_dict(self)


@err_chain(IAMResourceException)
def create_resource(
        auth_headers: dict[str, str],
        payload: dict[str, object] = None,
        name: str = None,
        display_name: str = None,
        tenant_id: str = None,
        application: str = None,
        path: str = None,
        resource_type: str = None,
        enabled: bool = True,
        description: str = None,
        metadata: Dict[str, object] = None
) -> Resource:
    url = IAMCORE_URL + "/api/v1/resources"
    if not payload:
        payload = {
            "name": name,
            "displayName": display_name,
            "tenantID": tenant_id,
            "application": application,
            "path": path,
            "resourceType": resource_type,
            "enabled": enabled,
            "description": description,
            "metadata": metadata
        }
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    response: Response = requests.request("POST", url, json=payload, headers=headers)
    return IamEntityResponse(Resource, **unwrap_post(response)).data


@err_chain(IAMResourceException)
def update_resource(
        auth_headers: dict[str, str],
        payload: dict[str, object] = None,
        resource_id: str = None,
        display_name: str = None,
        enabled: bool = True,
        description: str = None,
        metadata: Dict[str, object] = None
) -> None:
    if not auth_headers:
        raise IAMUnauthorizedException(f"Missing authorization headers")
    if not resource_id:
        raise IAMResourceException(f"Missing resource_id")
    url = IAMCORE_URL + "/api/v1/resources/" + IRN.of(resource_id).to_base64()
    if not payload:
        payload = {
            "displayName": display_name,
            "enabled": enabled,
            "description": description,
            "metadata": metadata
        }
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    response: Response = requests.request("PATCH", url, json=payload, headers=headers)
    unwrap_put(response)


@err_chain(IAMResourceException)
def delete_resource(auth_headers: dict[str, str], resource_id: str) -> None:
    if not auth_headers:
        raise IAMUnauthorizedException(f"Missing authorization headers")
    if not resource_id:
        raise IAMResourceException(f"Missing resource_id")

    url = IAMCORE_URL + "/api/v1/resources/" + IRN.of(resource_id).to_base64()
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    response: Response = requests.request("DELETE", url, data="", headers=headers)
    unwrap_delete(response)


@err_chain(IAMResourceException)
def delete_resources(auth_headers: dict[str, str], resources_ids: List[IRN]) -> None:
    if not auth_headers:
        raise IAMUnauthorizedException(f"Missing authorization headers")
    if not resources_ids:
        raise IAMResourceException(f"Missing resource_id")

    url = IAMCORE_URL + "/api/v1/resources/delete"
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    payload = {
        "resourceIDs": [
            IRN.of(r).to_base64()
            for r in resources_ids
            if r
        ]
    }
    response: Response = requests.request("POST", url, json=payload, headers=headers)
    unwrap_delete(response)


@err_chain(IAMResourceException)
def search_resource(
        headers: dict[str, str],
        irn: IRN = None,
        path: str = None,
        display_name: str = None,
        enabled: bool = None,
        tenant_id: str = None,
        application: str = None,
        resource_type: str = None,
        page: int = None,
        page_size: int = None,
        sort: str = None,
        sort_order: SortOrder = None
) -> IamEntitiesResponse[Resource]:
    url = IAMCORE_URL + "/api/v1/resources"

    querystring = {
        "irn": str(irn) if irn else None,
        "path": path,
        "application": application,
        "enabled": enabled,
        "displayName": display_name,
        "resourceType": resource_type,
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
    return IamEntitiesResponse(Resource, **unwrap_get(response))


@err_chain(IAMException)
def search_all_resources(auth_headers: dict[str, str], *vargs, **kwargs) -> Generator[Resource, None, None]:
    return generic_search_all(auth_headers, search_resource, *vargs, **kwargs)
