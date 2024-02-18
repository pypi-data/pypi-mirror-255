import logging
from typing import List, Generator, Union, Any

import requests
from iamcore.irn import IRN
from requests import Response

from iamcore.client.common import IamEntitiesResponse, generic_search_all
from iamcore.client.conf import IAMCORE_URL
from iamcore.client.exceptions import EVALUATE_MAPPING, unwrap_return_empty, IAMException, unwrap_return_json

logger = logging.getLogger(__name__)


def authorize(
        authorization_headers: dict[str, str],
        principal_irn: IRN,
        account_id: str,
        application: str,
        tenant_id: str,
        resource_type: str,
        resource_path: str,
        action: str,
        resource_ids: Union[List[str], None] = None) -> List[IRN]:
    if not action:
        raise IAMException("Action must be defined")
    tenant_id = tenant_id or principal_irn.tenant_id
    account_id = account_id or principal_irn.account_id
    if resource_ids:
        resources_irn_list = [
            IRN.create(
                account_id=account_id,
                application=application,
                tenant_id=tenant_id,
                resource_type=resource_type,
                resource_path=resource_path,
                resource_id=resource_id)
            for resource_id in resource_ids
        ]
        logger.debug(f"Going to evaluate {authorization_headers} {action} {resources_irn_list}")
        evaluate(authorization_headers, action, resources_irn_list)
        return resources_irn_list
    logger.debug("Going to evaluate by type")
    return list(evaluate_all_resources(authorization_headers, application, action, resource_type))


def evaluate(auth_headers: dict[str, str], action: str, resources: List[IRN]) -> None:
    url = IAMCORE_URL + "/api/v1/evaluate"
    payload = {
        "action": action,
        "resources": [str(r) for r in resources if r]
    }
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    logger.debug(f"Going to evaluate resources: POST {url}, json={payload}")
    response: Response = requests.request("POST", url, json=payload, headers=headers)
    return unwrap_return_empty(response, EVALUATE_MAPPING)


def evaluate_resources(
        auth_headers: dict[str, str],
        application: str,
        action: str,
        resource_type: str,
        page: int = 1,
        page_size: int = 100) -> IamEntitiesResponse[IRN]:
    url = IAMCORE_URL + "/api/v1/evaluate/resources"
    payload = {
        "application": application,
        "action": action,
        "resourceType": resource_type
    }
    querystring = {
        "page": page,
        "pageSize": page_size,
    }
    headers = {
        "Content-Type": "application/json",
        **auth_headers
    }
    logger.debug(f"Going to evaluate resource type: POST {url}, json={payload}, params={querystring}")
    response: Response = requests.request("POST", url, json=payload, headers=headers, params=querystring)
    return IamEntitiesResponse(IRN, **unwrap_return_json(response, EVALUATE_MAPPING))


def evaluate_all_resources(auth_headers: dict[str, str], *vargs, **kwargs) -> Generator[IRN, None, None]:
    return generic_search_all(auth_headers, evaluate_resources, *vargs, **kwargs)
