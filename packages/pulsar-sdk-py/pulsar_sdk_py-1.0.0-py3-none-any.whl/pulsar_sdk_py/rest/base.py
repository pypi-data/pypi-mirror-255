import re
import requests

from pulsar_sdk_py.exceptions import APIError


class PulsarRestClientAPI:
    """
    A helper class for making HTTP requests to a REST API.

    This class provides several methods for sending HTTP requests to Pulsar REST API endpoints.
    It includes a static method for filtering out any key-value pairs from a dictionary where the value is None,
    as well as a method for sending an HTTP request to a Pulsar REST API endpoint and returning the JSON
    response body.

    Attributes:
        headers (dict): A dictionary of headers to include in HTTP requests sent by instances of this class.

    """

    headers: dict
    REST_API_URL: str

    def __init__(self, rest_api_url: str, headers: dict):
        self.headers = headers
        self.REST_API_URL = rest_api_url

    def _request(self, path: str, request_type: str, request_body: dict | None = None, **kwargs):
        """
        Send an HTTP request to a specific REST API endpoint and return the JSON response body.

        Args:
            path (str): The name of a function that corresponds to a specific REST API endpoint.
            request_type (str): The HTTP method to use for the request (e.g. "GET", "POST", "PUT").
            request_body (dict, optional): The JSON payload to include in the request body (default: {}).
            **kwargs: Key-value pairs to include as path or query parameters in the request URL.

        Returns:
            dict: The JSON response body as a dictionary.

        Raises:
            HTTPError: If the response from the API endpoint indicates an error status code (e.g. 4xx or 5xx).

        """
        if request_body is None:
            request_body = {}

        # This code extracts named parameters from a string (endpoint_url) using regular expressions,
        # and populates them with corresponding values from a dictionary (kwargs).The resulting string is formed
        # by substituting the named parameters with their corresponding values, and concatenating the result with
        # another string (BASE_URL).
        param_names = re.findall(r"\{([^{}]*)\}", path)
        params = {}
        for param_name in param_names:
            if param_name not in kwargs:
                continue
            param_value = kwargs.pop(param_name)
            params[param_name] = param_value

        formatted_url = path.format(**params)
        full_path = self.REST_API_URL + formatted_url

        if kwargs:
            # If there are any remaining kwargs, construct them as query parameters for the endpoint URL
            query_params = []
            for key, value in kwargs.items():
                if isinstance(value, list):
                    query_params.extend(f"{key}={item}" for item in value)
                else:
                    query_params.append(f"{key}={value}")
            query_params_string = "&".join(query_params)
            full_path += f"?{query_params_string}"  # Add the query parameters to the endpoint URL

        response = requests.request(method=request_type, url=full_path, json=request_body, headers=self.headers)
        if 400 <= response.status_code < 600:
            msg = response.json()
            error_msg = msg.get("error", None)
            raise APIError(message=error_msg or msg, status_code=response.status_code)
        return response.json()
