import os
from typing import TYPE_CHECKING

import arrow
import jwt
import requests
from requests.exceptions import ConnectionError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from deci_platform_client.api_client import ApiClient as BaseApiClient

if TYPE_CHECKING:
    from typing import Optional, Union
    from uuid import UUID

    import urllib3
    from urllib3._collections import HTTPHeaderDict

    from deci_platform_client.configuration import Configuration


def calc_token_expiration(expiration):
    return arrow.utcnow().shift(seconds=expiration * 0.8)


class ApiClient(BaseApiClient):
    _DECI_WORKSPACE_HEADER = "x-deci-workspace"
    _AUTHORIZATION_HEADER = "Authorization"

    class _FronteggAuthenticator:
        __access_token_expiration = None
        session_request = requests.session()

        def __init__(self, client_id: str, api_key: str):
            if not client_id or not api_key:
                raise ValueError("client_id and api_key are required")
            self.client_id = client_id
            self.api_key = api_key
            self.access_token = None
            self.refresh_access_token()

        @property
        def should_refresh_vendor_token(self) -> bool:
            return (
                self.access_token is None
                or self.__access_token_expiration is None
                or arrow.utcnow() >= self.__access_token_expiration
            )

        @retry(stop=stop_after_attempt(5), wait=wait_fixed(0.5), retry=retry_if_exception_type(ConnectionError))
        def refresh_access_token(self) -> None:
            body = {"clientId": self.client_id, "secret": self.api_key}
            auth_base = os.environ.get("DECI_FRONTEGG_AUTH_SUB_DOMAIN", "deci")
            auth_url = f"https://{auth_base}.frontegg.com/identity/resources/auth/v1/api-token"

            auth_response = self.session_request.post(auth_url, json=body)
            auth_response.raise_for_status()
            response_body = auth_response.json()
            self.access_token = response_body["accessToken"]
            self.__access_token_expiration = calc_token_expiration(response_body["expiresIn"])

    def __init__(self, configuration: "Configuration"):
        super().__init__(configuration=configuration)
        self._frontegg_auth: "Optional[ApiClient._FronteggAuthenticator]" = None
        self.email = None
        self.workspace_id = None

    def _set_up_frontegg_header(self) -> None:
        self.default_headers[self._AUTHORIZATION_HEADER] = f"Bearer {self._frontegg_auth.access_token}"

    def set_up_frontegg_auth(self, *, client_id: str, secret: str) -> None:
        self._frontegg_auth = ApiClient._FronteggAuthenticator(client_id, secret)
        self._set_up_frontegg_header()
        decoded_token = jwt.decode(jwt=self._frontegg_auth.access_token, options={"verify_signature": False})
        self.email = decoded_token["email"]
        self.set_up_workspace_id(os.environ.get("DECI_WORKSPACE_ID", decoded_token["userMetadata"]["workspaces"][0]))

    def refresh_frontegg_auth(self) -> None:
        if not self._frontegg_auth:
            return
        self._frontegg_auth.refresh_access_token()

    def set_up_workspace_id(self, workspace_id: "Union[UUID, str]") -> None:
        self.workspace_id = str(workspace_id)
        self.default_headers[self._DECI_WORKSPACE_HEADER] = self.workspace_id

    def tear_down_frontegg_auth(self) -> None:
        self._frontegg_auth = None
        self.default_headers.pop(self._DECI_WORKSPACE_HEADER, None)
        self.default_headers.pop(self._AUTHORIZATION_HEADER, None)

    def call_api(
        self,
        resource_path: str,
        method: str,
        headers: "Optional[HTTPHeaderDict]" = None,
        body: "Optional[Union[str, bytes]]" = None,
        fields: "Optional[tuple[tuple[str, str], ...]]" = None,
        auth_settings: "Optional[list[str]]" = None,
        async_req: "Optional[bool]" = None,
        stream: bool = False,
        timeout: "Optional[Union[int, tuple]]" = None,
        host: "Optional[str]" = None,
    ) -> "urllib3.HTTPResponse":
        if self._frontegg_auth is not None and self._frontegg_auth.should_refresh_vendor_token:
            self._frontegg_auth.refresh_access_token()
            self._set_up_frontegg_header()
        return super().call_api(
            resource_path,
            method,
            headers,
            body,
            fields,
            auth_settings,
            async_req,
            stream,
            timeout,
            host,
        )
