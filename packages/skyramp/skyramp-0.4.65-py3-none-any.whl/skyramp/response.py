"""
Contains helpers for interacting with Skyramp mock response.
"""
import inspect
import json
from typing import Callable, Dict, List, Optional

from skyramp.endpoint import _Endpoint
from skyramp.rest_param import _RestParam

class _ResponseValue:
    """
    Represents a response value.
    """
    def __init__(self,
                 name: str,
                 endpoint_descriptor: _Endpoint,
                 method_type: Optional[str]=None,
                 method_name: Optional[str]=None,
                 blob: Optional[Dict] = None,
                 python_function: Optional[Callable] = None,
                 python_path: Optional[str] = None,
                 params: Optional[List[_RestParam]] = None,
                 headers: Optional[Dict] = None):
        """
        Create a new ResponseValue instance.

        Args:
            blob (Dict, optional): The response body as a JSON object.
            method_type (str, optional): The method type.
            method_name (str, optional): The method name.
            python_function (Callable, optional): The Python response as a function.
            python_path (str, optional): The path to a Python file.
            params (List[_RestParam], optional): An array of REST parameters.
            headers (Dict, optional): A dictionary of key-value pairs for headers.
        """
        self.name = name
        self.endpoint_descriptor = endpoint_descriptor
        if method_type is not None:
            self.method_type = method_type
        if method_name is not None:
            self.method_name = method_name
        if blob is not None:
            self.blob = blob
        if python_function is not None:
            self.python_function = inspect.getsource(python_function)
        if python_path is not None:
            self.python_path = python_path
        if params is not None:
            self.params = params
        if headers is not None:
            self.headers = headers
        self.traffic_config = None
        self.proxy_live_service = False
        self.response_value = None
        self.cookie_value = None

    def set_traffic_config(self, traffic_config):
        """ Set the traffic config. """
        self.traffic_config = traffic_config

    def enable_proxy_live_service(self):
        """ Enable proxy live service. """
        self.proxy_live_service = True

    def set_value(self, response_value: json):
        """
        Sets the response value for this step
        """
        self.response_value = response_value

    def set_cookie_value(self, cookie_value: json):
        """
        Sets the cookie value for this step
        """
        self.cookie_value = cookie_value

    def to_json(self):
        """
        Convert the object to a JSON string.
        """
        if hasattr(self, 'method_name') and self.method_name is not None:
            method_name = self.method_name
        if hasattr(self, 'method_type') and self.method_type is not None:
            method_name = self.endpoint_descriptor.get_method_name_for_method_type(self.method_type)
        response = {
            "name": self.name,
            "endpointName": self.endpoint_descriptor.endpoint.get("name"),
            "methodName": method_name,
        }
        if hasattr(self, 'blob') and self.blob is not None:
            response["blob"] = self.blob
        if hasattr(self, 'python_path') and self.python_path is not None:
            response["pythonPath"] = self.python_path
        if hasattr(self, 'python_function') and self.python_function is not None:
            response["python"] = self.python_function
        if hasattr(self, 'params') and self.params is not None:
            response["params"] = [param.to_json() for param in self.params]
        if hasattr(self, 'headers') and self.headers is not None:
            response["headers"] = self.headers

        return response
    