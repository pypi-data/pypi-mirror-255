"""Module with session for authenticated requests to server."""
import os
import posixpath
from http import HTTPStatus

import requests
from requests import Response
from sgqlc.endpoint.http import HTTPEndpoint
from sgqlc.operation import Operation
from websocket import WebSocket, create_connection

from ML_management.mlmanagement.base_exceptions import MLMClientError
from ML_management.mlmanagement.singleton_pattern import Singleton
from ML_management.mlmanagement.variables import _get_server_ml_api, _get_server_url


class InvalidCredentialsError(MLMClientError):
    """Exception for invalid login-password pair."""

    pass


class MissedEnvVarError(MLMClientError):
    """Exception for the case of the absence of the necessary environment variable."""

    pass


class InvalidEnvVarError(MLMClientError):
    """Exception for the case of the invalid value of environment variable."""

    pass


class AuthSession(metaclass=Singleton):
    """Extend the standard session functionality with authentication functionality."""

    def __init__(self) -> None:
        server_url = _get_server_url()
        if server_url is None:
            raise MissedEnvVarError("You must specify environment variable server_url.")
        if not server_url.startswith("http"):
            raise InvalidEnvVarError("$server_url must starts with http or https.")

        self.cookies = {}
        # check mlflow endpoint is available without authentication
        if requests.get(_get_server_ml_api()).status_code == HTTPStatus.METHOD_NOT_ALLOWED:
            return
        if self._try_set_cookies():
            return
        login, password = os.getenv("login"), os.getenv("password")
        if not self._try_authenticate_by_credentials(login, password):
            raise InvalidCredentialsError(f"User with login {login} and password {password} does not exist.")

    def get(self, url: str, **kwargs) -> Response:
        """Proxy requests.get."""
        response = requests.get(url, cookies=self.cookies, **kwargs)
        # if token was updated, update our cookie
        self._update_cookies(response, ["kc-access"])
        return response

    def post(self, url: str, **kwargs) -> Response:
        """Proxy requests.post."""
        response = requests.post(url, cookies=self.cookies, **kwargs)
        # if token was updated, update our cookie
        self._update_cookies(response, ["kc-access"])
        return response

    # For sdk auth purposes
    def sgqlc_request(self, operation: Operation) -> dict:
        """Make request to /graphql for operation."""
        cookie_header = self._get_cookie_header()
        return HTTPEndpoint(posixpath.join(_get_server_url(), "graphql"), base_headers={"Cookie": cookie_header})(
            operation
        )

    def instantiate_websocket_connection(self, url: str) -> WebSocket:
        """Create websocket connection."""
        ws = create_connection(url, cookie=self._get_cookie_header())
        return ws

    def _update_cookies(self, response: Response, cookie_names: list) -> None:
        """Update cookies from cookie_names list."""
        for cookie_name in cookie_names:
            if cookie := response.cookies.get(cookie_name):
                self.cookies[cookie_name] = cookie

    def _get_cookie_header(self) -> str:
        return "; ".join(f"{cookie_name}={cookie_value}" for cookie_name, cookie_value in self.cookies.items())

    def _try_set_cookies(self) -> bool:
        kc_access, kc_state = os.getenv("kc_access"), os.getenv("kc_state")
        if kc_access is not None and kc_state is not None:
            for name, value in zip(["kc-access", "kc-state"], [kc_access, kc_state]):
                self.cookies[name] = value
            return True
        return False

    def _try_authenticate_by_credentials(self, login, password) -> bool:
        if login is None or password is None:
            return False
        response = requests.post(
            posixpath.join(_get_server_url(), "oauth", "login"), data={"username": login, "password": password}
        )
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            return False
        if response.status_code != HTTPStatus.OK:
            response.raise_for_status()
        self.cookies = {
            "kc-state": response.cookies["kc-state"],
            "kc-access": response.cookies["kc-access"],
        }
        return True
