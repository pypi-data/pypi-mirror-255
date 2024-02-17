import logging
import json

import requests
from abc import abstractmethod
from http import HTTPStatus
from contextlib import suppress

from requests import ConnectionError, Response

import robotcloud.constants
import robotcloud.exceptions as exceptions
from robotcloud.authenticator import (
    Authenticator,
    BasicAuthenticator,
    BearerAuthenticator
)
from robotcloud.constants import DEFAULT_TIMEOUT
from robotcloud.exceptions import RequestConnectionError

log = logging.getLogger(__name__)


def json_from_response(response: Response):
    if response.ok:
        return response.json()

    status_code = int(response.status_code)
    try:
        __print_error(response)
        response_message = response.json()["message"]
    except ValueError:
        response_message = f"Undefined error (code: {status_code})."

    if status_code == HTTPStatus.UNAUTHORIZED:
        raise exceptions.UnauthorizedAccessError(response_message)
    elif status_code == HTTPStatus.FORBIDDEN:
        raise exceptions.ForbiddenError(response_message)
    elif status_code == HTTPStatus.NOT_FOUND:
        raise exceptions.NotFoundError(response_message)
    elif status_code == HTTPStatus.BAD_REQUEST:
        raise exceptions.BadRequestError(response_message)
    elif status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        raise exceptions.InternalServerError(response_message)
    else:
        raise exceptions.RobotcloudRequestError(response_message)


def __print_error(response: Response):
    error = (
        f"\n{'<ERROR: Robotcloud API call>':*^75}"
        f"\n# [{response.request.method}] {response.request.url}"
        f"\n# {response}"
    )

    with suppress(TypeError):
        error += (
            f"\n{json.dumps(response.json(), indent=4)}"
        )

    error += (
        f"\n{'</ERROR: Robotcloud API call>':*^75}\n"
    )
    log.info(error)


class APIRequestHeader:

    def __init__(self, authenticator: Authenticator):
        self.items = {
            "x-api-key": robotcloud.constants.API_KEY,
            'Accept': 'application/json'
        }
        self.authenticator = authenticator

    @property
    def authenticator(self):
        return self._authenticator

    @authenticator.setter
    def authenticator(self, authenticator):
        self._authenticator = authenticator
        self.items["Authorization"] = authenticator.compute_string()


class APIEndPoint:
    ROOT_URL = robotcloud.constants.ROOT_URL

    def __init__(self, headers: dict):
        self.headers = headers

    def get(self, **kwargs):
        try:
            response = requests.request(url=self.url, method="GET", headers=self.headers,
                                        timeout=DEFAULT_TIMEOUT, **kwargs)
        except ConnectionError as e:
            log.exception(f"Get Request Connection error: {self.url}")
            raise RequestConnectionError(str(e))

        return json_from_response(response)

    def post(self, data, **kwargs):
        headers = self.headers.copy()
        headers['Content-Type'] = 'application/json'
        try:
            response = requests.request(url=self.url, method="POST", headers=headers, timeout=DEFAULT_TIMEOUT,
                                        data=json.dumps(data), **kwargs)
        except ConnectionError as e:
            log.exception(f"Post Request Connection error: {self.url}")
            raise RequestConnectionError(str(e))

        return json_from_response(response)

    def put(self, data):
        headers = self.headers.copy()
        headers['Content-Type'] = 'application/json'

        try:
            response = requests.request(url=self.url, method="PUT", headers=headers, timeout=DEFAULT_TIMEOUT,
                                        data=json.dumps(data))
        except ConnectionError as e:
            log.exception(f"Put Request Connection error: {self.url}")
            raise RequestConnectionError(str(e))
        return json_from_response(response)

    def delete(self):
        try:
            response = requests.request(url=self.url, method="DELETE", timeout=DEFAULT_TIMEOUT, headers=self.headers)
        except ConnectionError as e:
            log.exception(f"Delete Request Connection error: {self.url}")
            raise RequestConnectionError(str(e))
        return json_from_response(response)

    @property
    def url(self):
        return self.ROOT_URL + "/" + self.get_endpoint()

    @abstractmethod
    def get_endpoint(self):
        pass


class APIEndPointAuthenticated(APIEndPoint):
    def __init__(self, token: str):
        authenticator = BearerAuthenticator(token)
        self.header = APIRequestHeader(authenticator)
        super().__init__(self.header.items)

    @abstractmethod
    def get_endpoint(self):
        pass


class APIEndPointUnAuthenticated(APIEndPoint):
    def __init__(self, username: str, password: str):
        authenticator = BasicAuthenticator(username, password)
        self.header = APIRequestHeader(authenticator)
        super().__init__(self.header.items)

    @abstractmethod
    def get_endpoint(self):
        pass
