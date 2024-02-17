import logging
from platform import python_version

from requests import Response
from requests.adapters import HTTPAdapter
from requests.sessions import Session

from .number_lookup import NUMBER_LOOKUP
from .slack import SLACK
from .sms import SMS
from .verify import VERIFY
from .viber import VIBER

import direct7

from .errors import *
from .whatsapp import WHATSAPP

log = logging.getLogger(__name__)

try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


class Client:

    def __init__(
            self,
            api_token=None,
            timeout=30,
            pool_connections=10,
            pool_maxsize=10,
            max_retries=3
    ) -> None:
        self._api_token = api_token
        self._host = "https://api.d7networks.com"

        user_agent = f"direct7-python-sdk/{direct7.__version__} python/{python_version()}"

        self.headers = {
            "User-Agent": user_agent,
            "Accept": "application/json",
        }

        self.sms = SMS(self)
        self.verify = VERIFY(self)
        self.viber = VIBER(self)
        self.slack = SLACK(self)
        self.number_lookup = NUMBER_LOOKUP(self)
        self.whatsapp = WHATSAPP(self)

        self.timeout = timeout
        self.session = Session()
        self.adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=max_retries,
        )
        self.session.mount("https://", self.adapter)

    def _create_bearer_token_string(self):
        return f"Bearer {self._api_token}"

    # Gets and sets _host attribute
    def host(self, value=None):
        if value is None:
            return self._host
        else:
            self._host = value

    @staticmethod
    def process_response(host, response: Response):
        """
        Process the response from the D7 API.
        """
        log.debug(f"Response headers {repr(response.headers)}")
        if response.status_code == 401:
            raise AuthenticationError("Invalid API token")
        elif 200 <= response.status_code < 300:
            # success response
            try:
                result = response.json()
                log.debug(f"Successful process response: {result}")
                return result
            except JSONDecodeError:
                pass
        elif 400 <= response.status_code < 500:
            log.warning(f"Client error: {response.status_code} {repr(response.content)}")
            if response.status_code == 400:
                raise BadRequest(f"{repr(response.content)}")
            if response.status_code == 404:
                raise NotFoundError(f"{repr(response.content)}")
            if response.status_code == 402:
                raise InsufficientCreditError(f"{repr(response.content)}")
            if response.status_code == 422:
                raise ValidationError(f"{repr(response.content)}")
            else:
                raise ClientError(f"{response.status_code} response from {host}")
        elif 500 <= response.status_code < 600:
            log.warning(f"Server error: {response.status_code} {repr(response.content)}")
            message = f"{response.status_code} response from {host}"
            raise ServerError(message)

    def get(self, host, path, params=None):
        """
        Send HTTP POST request to the D7 API.
        """
        request_url = f"{host}{path}"
        self._request_headers = self.headers
        self._request_headers['Authorization'] = self._create_bearer_token_string()
        log.debug(f"GET request sent to {request_url} with headers {self._request_headers} and params {params}")
        return self.process_response(host,
                                     self.session.get(
                                         request_url,
                                         headers=self._request_headers,
                                         params=params,
                                         timeout=self.timeout
                                     )
                                     )

    def post(self, host, path, body_is_json=True, params={}):
        """
        Send HTTP POST request to the D7 API.
        """
        request_url = f"{host}{path}"
        self._request_headers = self.headers
        self._request_headers['Authorization'] = self._create_bearer_token_string()
        if body_is_json:
            self._request_headers['Content-Type'] = 'application/json'
            log.debug(f"POST request sent to {request_url} with headers {self._request_headers} and params {params}")
            return self.process_response(host,
                                         self.session.post(
                                             request_url,
                                             headers=self._request_headers,
                                             json=params,
                                             timeout=self.timeout
                                         )
                                         )
        else:
            self._request_headers['Content-Type'] = 'application/x-www-form-urlencoded'
            return self.process_response(host,
                                         self.session.post(
                                             request_url,
                                             headers=self._request_headers,
                                             data=params,
                                             timeout=self.timeout
                                         )
                                         )

    def put(self, path, data=None):
        ...

    def delete(self, path, data=None):
        ...

    def patch(self, path, data=None):
        ...
