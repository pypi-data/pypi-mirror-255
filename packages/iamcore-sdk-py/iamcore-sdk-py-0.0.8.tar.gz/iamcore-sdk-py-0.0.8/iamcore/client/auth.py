import http.client
from uuid import UUID

import requests

from .exceptions import IAMException, IAMUnauthorizedException
from iamcore.client.conf import IAMCORE_ISSUER_URL


class TokenResponse:
    access_token: str
    expires_in: int
    refresh_expires_in: int
    refresh_token: int
    token_type: str
    not_before_policy: int
    session_state: UUID
    scope: str

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if '-' in k:
                setattr(self, k.replace("-", "_"), v)
            else:
                setattr(self, k, v)

    @property
    def access_headers(self) -> dict[str, str]:
        return {
            "Authorization": "Bearer " + self.access_token
        }


def get_api_key_auth_headers(api_key: str):
    return {
        'X-iamcore-API-Key': api_key
    }


def get_token_with_password(realm: str, client_id, username: str, password: str, issuer_url=None) -> TokenResponse:
    if not issuer_url:
        issuer_url = IAMCORE_ISSUER_URL.strip()
    url = f"{issuer_url}/realms/{realm}/protocol/openid-connect/token"
    payload = f"grant_type=password&client_id={client_id}&username={username}&password={password}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    try:
        response = requests.request("POST", url, data=payload, headers=headers)
        if response.status_code == http.client.OK:
            return TokenResponse(**response.json())
        elif response.status_code == http.client.UNAUTHORIZED:
            raise IAMUnauthorizedException(f"Unauthorized: {response.json()}")
        raise IAMUnauthorizedException(f"Unexpected error code: {response.status_code}")
    except IAMException as e:
        raise e
    except Exception as e:
        raise IAMException(f"Failed to get auth token with exception: {e}")
