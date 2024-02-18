from typing import Generator, Union

import requests
from iamcore.irn import IRN
from requests import Response

from iamcore.client.common import to_snake_case, to_dict, generic_search_all, IamEntitiesResponse
from iamcore.client.conf import IAMCORE_URL
from iamcore.client.exceptions import err_chain, IAMException, unwrap_get


class ApplicationApiKey:
    api_key: str
    state: str
    last_used: str
    created: str
    updated: str

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            attr = to_snake_case(k)
            setattr(self, attr, v)

    @staticmethod
    def of(item):
        if isinstance(item, ApplicationApiKey):
            return item
        elif isinstance(item, list):
            return [ApplicationApiKey.of(i) for i in item]
        elif isinstance(item, dict):
            return ApplicationApiKey(**item)
        raise IAMException(f"Unexpected response format")

    def to_dict(self):
        return to_dict(self)


@err_chain(IAMException)
def get_application_api_keys(headers: dict[str, str], irn: Union[str, IRN],
                             page: int = 1) -> IamEntitiesResponse[ApplicationApiKey]:
    if isinstance(irn, IRN):
        irn = irn.to_base64()
    if isinstance(irn, str):
        irn = IRN.of(irn).to_base64()

    url = f"{IAMCORE_URL}/api/v1/applications/{irn}/api-keys?page={page}"
    response: Response = requests.request("GET", url, data="", headers=headers)
    return IamEntitiesResponse(ApplicationApiKey, **unwrap_get(response))


@err_chain(IAMException)
def get_all_applications_api_keys(auth_headers: dict[str, str], *vargs, **kwargs) -> Generator[ApplicationApiKey, None, None]:
    return generic_search_all(auth_headers, get_application_api_keys, *vargs, **kwargs)
