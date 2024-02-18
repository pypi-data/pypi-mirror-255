"""
Contains helpers for interacting with Skyramp test request.
"""
import inspect
import json
from typing import Callable, Optional
from skyramp.endpoint import _Endpoint
from skyramp.rest_param import _RestParam as RestParam

class _Request:
    def __init__(self,
                 name: str,
                 endpoint_descriptor: _Endpoint,
                 method_type: Optional[str]=None,
                 method_name: Optional[str]=None,
                 params: Optional[RestParam]=None,
                 blob: Optional[str]=None,
                 headers: Optional[dict]=None,
                 vars_: Optional[dict]=None,
                 python_path: Optional[str]=None,
                 python_function: Optional[Callable]=None) -> None:
        self.name = name
        self.endpoint_descriptor = endpoint_descriptor
        if method_type is not None:
            self.method_type = method_type
        if params is not None:
            self.params = params
        if blob is not None:
            self.blob = blob
        if python_path is not None:
            self.python_path = python_path
        if python_function is not None:
            self.python_function = inspect.getsource(python_function)
        if headers is not None:
            self.headers = headers
        if vars_ is not None:
            self.vars_ = vars_
        if method_name is not None:
            self.method_name = method_name
        self.cookie_value = None

    def set_cookie_value(self, cookie_value: json):
        """
        Sets the cookie value for this step
        """
        self.cookie_value = cookie_value

    def to_json(self):
        """
        Convert the object to a JSON string.
        """
        return {
            "requestName": self.name
        }

    def as_request_dict(self, global_headers=None):
        """
        Convert the object to a JSON string.
        """

        descriptor = self.endpoint_descriptor
        endpoint = descriptor.endpoint
        endpoint_name = endpoint.get("name")
        if not endpoint_name:
            raise Exception(f"endpoint name not found. Endpoint descriptor: {descriptor}")

        if hasattr(self, 'method_name') and self.method_name is not None:
            method_name = self.method_name
        if hasattr(self, 'method_type') and self.method_type is not None:
            method_name = descriptor.get_method_name_for_method_type(self.method_type)
        request_dict = {
            "name": self.name,
            "endpointName": endpoint_name,
            "methodName": method_name,
        }

        if global_headers is not None or self.headers is not None:
            request_dict["headers"] = {}
        if global_headers is not None:
            request_dict["headers"] = global_headers
        if hasattr(self, 'headers') and  self.headers is not None:
            request_dict["headers"] = request_dict["headers"] | self.headers
        if hasattr(self, 'params') and  self.params is not None:
            params = [param.to_json() for param in self.params]
            request_dict["params"] = params
        if hasattr(self, 'blob') and self.blob is not None:
            request_dict["blob"] = self.blob
        if hasattr(self, 'python_path') and self.python_path is not None:
            request_dict["pythonPath"] = self.python_path
        if hasattr(self, 'python_function') and self.python_function is not None:
            request_dict["python"] = self.python_function
        if hasattr(self, 'vars_') and self.vars_ is not None:
            request_dict["vars"] = self.vars_
        self._set_overrides(request_dict)

        return request_dict

    def _set_overrides(self, request_dict: dict):
        """
        Sets the override value for this step
        """
        if hasattr(self, 'cookie_value') and self.cookie_value is not None:
            request_dict["cookies"] = self.cookie_value
