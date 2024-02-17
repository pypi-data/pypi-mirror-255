import requests
from requests.exceptions import ConnectionError
from rmbcommon.exceptions.client import (
    ServerConnectionError,
    ServerError,
)
from rmbcommon.exceptions.client import raise_exception_by_code
from rmbclient.log import log


class APIRequest:
    def __init__(self, api_url="http://127.0.0.1:5001",
                 token="", debug=False):
        self.api_url = api_url
        self.token = token
        self.debug = debug

    def _handle_request(self, method, url, headers, json=None, params=None, files=None):
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=json, files=files)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError("Unsupported HTTP method")
        return response

    def send(self, endpoint, method, data=None, params=None, files=None) -> dict or None:

        headers = {"Authorization": f"Bearer {self.token}"}
        url = f"{self.api_url}{endpoint}"

        try:
            response = self._handle_request(
                method, url, headers, json=data, params=params, files=files
            )
        except ConnectionError:
            raise ServerConnectionError(f"Server {url} Connection Error")

        if response.status_code in (200, 201):
            if method == 'DELETE':
                return True
            else:
                return response.json()

        log_record = {
            'status': response.status_code,
            'response': str(response),
            'method': method,
            'endpoint': endpoint,
            'data': data,
        }
        log.info(f"API Request Failed: {log_record}")

        try:
            res_dict = response.json()
        except Exception as e:
            raise ServerError(f"Server Unknown Error: {e} {str(response)}")

        raise_exception_by_code(res_dict['code'], res_dict['message'])
