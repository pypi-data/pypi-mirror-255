import requests


class SellPathHttpClient:
    def __init__(self, app_type, api_key=None, base_url=None):
        """
        Initialize the Client Manager with a specific tenant ID and available tools.
        """
        self.app_type = app_type
        self.api_key = api_key
        self.base_url = base_url

    def __repr__(self):
        return "sellpath_http_client"

    @property
    def type(self):
        return "sellpath_http_client"

    def get(self, path, params={}):
        """
        Perform a GET request to the Apollo API.

        Args:
            path (str): API endpoint path.
            params (dict): Query parameters.

        Returns:
            dict: Dictionary containing response information including headers, status code, and body.
        """
        return self._http_request("get", path, params=params)

    def post(self, path, params={}, body={}):
        """
        Perform a POST request to the Apollo API.

        Args:
            path (str): API endpoint path.
            params (dict): Query parameters.
            body (dict): Request body.

        Returns:
            dict: Dictionary containing response information including headers, status code, and body.
        """
        return self._http_request("post", path, params=params, body=body)

    def patch(self, path, params={}, body={}):
        """
        Perform a PATCH request to the Apollo API.

        Args:
            path (str): API endpoint path.
            params (dict): Query parameters.
            body (dict): Request body.

        Returns:
            dict: Dictionary containing response information including headers, status code, and body.
        """
        return self._http_request("patch", path, params=params, body=body)

    def put(self, path, params={}, body={}):
        """
        Perform a PUT request to the Apollo API.

        Args:
            path (str): API endpoint path.
            params (dict): Query parameters.
            body (dict): Request body.

        Returns:
            dict: Dictionary containing response information including headers, status code, and body.
        """
        return self._http_request("put", path, params=params, body=body)

    def delete(self, path, params={}):
        """
        Perform a DELETE request to the Apollo API.

        Args:
            path (str): API endpoint path.
            params (dict): Query parameters.

        Returns:
            dict: Dictionary containing response information including headers, status code, and body.
        """
        return self._http_request("delete", path, params=params)

    def _http_request(self, method, path, params={}, body={}):
        if self.app_type == "apollo":
            return self._apollo_http_request(method=method, path=path, params=params, body=body)
        else:
            return self._normal_http_request(method=method, path=path, params=params, body=body)

    def _normal_http_request(self, method, path, params={}, body={}):  # -> dict:
        available_http_method = ["get", "post", "patch", "put", "delete"]
        method = method.lower()
        if method not in available_http_method:
            raise Exception(f"not available method {method}")
        request_method = getattr(requests, method)

        base_url = self.base_url
        url = base_url + ("/" + path if not path.startswith("/") else path)

        if method.lower() == "get":
            response = request_method(url, params=params)
        else:
            response = request_method(url, params=params, json=body)
            # return response
        return response.json()
        # result = Result(response)
        # return result
        # result = {}
        # result["headers"] = dict(response.headers)
        # result["status_code"] = response.status_code
        # try:
        #     result["body"] = response.json()

        # except Exception:
        #     result["body"] = response.content
        # return result

    def _apollo_http_request(self, method, path, params={}, body={}):  # -> dict:
        """
        Perform an HTTP request to the Apollo API.

        Args:
            method (str): HTTP method (get, post, patch, put, delete).
            path (str): API endpoint path.
            params (dict): Query parameters.
            body (dict): Request body.
            raw (bool): Flag indicating whether to return raw response or JSON.
        Returns:
            dict: Dictionary containing response information including headers, status code, and body.
        Raises:
            Exception: If an invalid HTTP method is provided.
        """
        available_http_method = ["get", "post", "patch", "put", "delete"]
        method = method.lower()
        apollo_api_key = self.api_key
        if method not in available_http_method:
            raise Exception(f"not available method {method}")
        request_method = getattr(requests, method)

        base_url = self.base_url
        url = base_url + ("/" + path if not path.startswith("/") else path)

        if method.lower() == "get":
            params["api_key"] = apollo_api_key
            response = request_method(url, params=params)
        else:
            body["api_key"] = apollo_api_key
            response = request_method(url, params=params, json=body)
            # return response
        return response.json()
        # result = Result(response)
        # return result

class Result:
    def __init__(self, response):
        self.headers = dict(response.headers)
        self.status_code = response.status_code
        try:
            self._body = response.json()
        except Exception:
            self._body = response.content

    @property
    def body(self):
        return self._body

    @property
    def content(self):
        return self._body

    def json(self):
        return self._body

    def result(self):
        return self._body

    def __getitem__(self, key):
        available_key = ["body", "content", "json", "result"]
        if key in available_key:
            return self._body
        if key == "headers":
            return self.headers
        if key == "status_code":
            return self.status_code
        else:
            raise KeyError(f"Key '{key}' not found.")
