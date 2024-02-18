"""
Defines a Skyramp client, which can be used to interact with a cluster.
"""

import ctypes
import json
from typing import List, Union
import yaml

from skyramp.utils import _library, _call_function, add_unique_items
from skyramp.scenario import _Scenario
from skyramp.endpoint import _Endpoint
from skyramp.test_description import _TestDescription
from skyramp.test_request import _Request
from skyramp.utils import SKYRAMP_YAML_VERSION
from skyramp.response import _ResponseValue
from skyramp.mock_description import _MockDescription
from skyramp.traffic_config import _TrafficConfig
class _ClientBase:
    """
    Client base class.
    """
    def __init__(self):
        self.project_path = None
        self.global_headers = {}

    def mocker_apply(self, namespace: str, address: str, endpoint) -> None:
        """
        Applies a mock configuration to K8s if `namespace` is provided,
        or to docker if `address` is provided.

        Args:
            namespace: The namespace where Mocker resides
            address: The address of Mocker
            endpoint: The Skyramp enpdoint object
        """
        yaml_string = yaml.dump(endpoint.mock_description)

        func = _library.applyMockDescriptionWrapper
        argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]

        _call_function(
            func,
            argtypes,
            ctypes.c_char_p,
            [
                namespace.encode(),
                address.encode(),
                yaml_string.encode(),
            ],
        )

    def mocker_apply_v1(
            self,
            namespace: str,
            address: str,
            response: Union[_ResponseValue, List[_ResponseValue]],
            traffic_config: _TrafficConfig=None,
            ) -> None:
        """
        Applies mock configuration to K8s if `namespace` is provided,
        or to docker if `address` is provided.

        Args:
            namespace: The k8s namespace where Mocker resides
            address: The docker address where Mocker resides
            response: The responses to apply to Mocker
            traffic_config: Traffic config
        """
        responses = response
        if isinstance(responses, _ResponseValue):
            responses = [responses]
        if isinstance(responses, list):
            mock_description = self.get_mock_description_v1(responses, traffic_config)
            yaml_string = yaml.dump(mock_description.to_json())

            func = _library.applyMockDescriptionWrapper
            argtypes = [
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.c_char_p,
            ]

            _call_function(
                func,
                argtypes,
                ctypes.c_char_p,
                [
                    namespace.encode(),
                    address.encode(),
                    yaml_string.encode(),
                ],)

    def set_project_directory(self, path: str) -> None:
        """
        Sets the project directory for the client.

        Args:
            path: The path to the project directory
        """
        self.project_path = path
        func = _library.setProjectDirectoryWrapper
        argtypes = [ctypes.c_char_p]
        restype = ctypes.c_char_p

        return _call_function(func, argtypes, restype, [path.encode()])

    def load_endpoint(self, name: str) -> _Endpoint:
        """
        Loads an endpoint from a file.

        Args:
            name: The name of the endpoint
        """
        if not self.project_path:
            raise Exception("project path not set")
        func = _library.getEndpointFromProjectWrapper
        argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        restype = ctypes.c_char_p

        endpoint_data = _call_function(
            func,
            argtypes,
            restype,
            [
                name.encode(),
                self.project_path.encode(),
            ],
            True,
        )
        if not endpoint_data:
            raise Exception(f"endpoint {name} not found")
        try:
            endpoint = json.loads(endpoint_data)
        except json.JSONDecodeError:
            raise ValueError(f"Endpoint data for {name} is not valid JSON")
        return _Endpoint(json.dumps(endpoint))

    def tester_start_v1(
            self,
            scenario: Union[_Scenario, List[_Scenario]],
            global_headers: map=None,
            namespace: str='',
            address: str='',
            test_name: str='',
            blocked=False,
            global_vars: map=None,
           ) -> str:
        """
        Runs testers. If namespace is provided, connects with the worker instance running
        on the specified namespace in the registered Kubernetes cluster. If address is provided,
        connects to the worker directly using the network address.

        Args:
            scenario: Scenario object for the test to run
            global_headers: Global headers to be used for all requests
            namespace: The namespace where mocker resides
            address: The address to reach mocker
            test_name: The name of the test
            blocked: Whether to wait for the test to finish
            global_vars: Global variables to be used for all requests

        Returns:
            The status of the test
        """
        if scenario is None:
            raise Exception("no scenario provided")

        if isinstance(scenario, list):
            test_description = _TestDescription(
                version= SKYRAMP_YAML_VERSION,
                test= {
                    "testPattern": [],
                },
                scenarios=[],
                services=[],
                requests=[],
                endpoints=[],
            )
            for test_scenario in scenario:
                test_desc = self.get_test_description_v1(test_scenario)
                add_unique_items(test_description.services, test_desc.services)
                add_unique_items(test_description.endpoints, test_desc.endpoints)
                add_unique_items(test_description.requests, test_desc.requests)

                add_unique_items(test_description.scenarios, test_desc.scenarios)
                # combine all the test patterns into one test_description
                test_pattern = test_desc.test["testPattern"]
                add_unique_items(test_description.test["testPattern"], test_pattern)
        else:
            test_description = self.get_test_description_v1(scenario)

        test_description.test["name"] = test_name

        if global_vars is not None:
            test_description.test["globalVars"] = global_vars

        # combine all the scenarios into one test_description
        _call_function(
            _library.runTesterStartWrapperWithGlobalHeaders,
            [
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.c_bool,
                ctypes.c_bool
            ],
            ctypes.c_char_p,
            [
                namespace.encode(),
                address.encode(),
                yaml.dump(test_description).encode(),
                test_name.encode(),
                json.dumps(global_headers).encode(),
                True,
                address is not None,
            ],
        )
        if blocked:
            tester_status_raw = _call_function(
                _library.runTesterStatusWrapper,
                [ctypes.c_char_p, ctypes.c_char_p],
                ctypes.c_char_p,
                [namespace.encode(), address.encode()],
                return_output=True,
            )

            tester_status = ""
            try:
                tester_status = json.loads(tester_status_raw)
            except ValueError as error:
                raise Exception(f"Could not parse tester status: {error}")

            if "status" not in tester_status:
                raise Exception(f"Could not parse tester status: {tester_status}")

            if tester_status["status"] == "finished":
                return

            if "error" in tester_status:
                raise Exception(f"Test failed: {tester_status['error']}")

            if "message" in tester_status:
                raise Exception(f"Test failed: {tester_status['message']}")

            raise Exception("Test failed")

    def set_global_rest_headers(self, global_headers) -> None:
        """
        Sets the global REST headers for this client.
        
        Args:
            global_headers: The global headers to set
        """
        self.global_headers=global_headers

    def get_mock_description_v1(
            self,
            responses: List[_ResponseValue],
            traffic_config: _TrafficConfig) -> _MockDescription:
        """
        Helper for returning the mock description for the response

        Args:
            responses: The responses to mock
            traffic_config: Traffic config
        """
        mock = {
            "responses": [],
            "proxies": [],
        }
        response_dict = {}
        service_dict = {}
        endpoint_dict = {}
        if traffic_config is not None:
            mock.update(traffic_config.to_json())
        mock_res = mock["responses"]
        for response in responses:
            if isinstance(response, _ResponseValue):
                response_json = response.to_json()
                # if the response is a proxy live service, add it to the proxies list
                if response.proxy_live_service:
                    mock["proxies"].append({
                    "endpointName": response.endpoint_descriptor.endpoint.get("name"),
                    "methodName": response.method_name,
                })
                response_dict[response.name] = response_json
                if response.response_value is not None:
                    response_dict[response.name]["override"] = response.response_value
                if response.cookie_value is not None:
                    response_dict[response.name]["cookies"] = response.cookie_value
                res = {
                    "responseName": response.name,
                }
                if response.traffic_config is not None:
                    res.update(response.traffic_config.to_json())
                mock_res.append(res)

                for service in response.endpoint_descriptor.services:
                    service_dict[service.get("name")] = service
                endpoint = response.endpoint_descriptor.endpoint
                endpoint_dict[endpoint.get("name")] = endpoint

        # All of the endpoints and services are within the response object
        return _MockDescription(
            version=SKYRAMP_YAML_VERSION,
            mock=mock,
            services=list(service_dict.values()),
            responses=list(response_dict.values()),
            endpoints=list(endpoint_dict.values()),
            )

    def get_test_description_v1(self, scenario: _Scenario) -> _TestDescription:
        """
        Helper for returning the test description for the scenario

        Args:
            scenario: The scenario to test

        Returns:
            The test description
        """
        steps = []
        request_dict = {}
        service_dict = {}
        endpoint_dict = {}

        for step_v1 in scenario.steps_v1:
            step = step_v1.to_json()
            if step_v1.response_value is not None:
                step["override"] = step_v1.response_value
            if step_v1.cookie_value is not None:
                step["cookies"] = step_v1.cookie_value
            steps.append(step)

            if isinstance(step_v1.step, _Request):
                request_dict[step_v1.step.name] = step_v1.step.as_request_dict(self.global_headers)

                for service in step_v1.step.endpoint_descriptor.services:
                    service_dict[service.get("name")] = service
                endpoint = step_v1.step.endpoint_descriptor.endpoint
                endpoint_dict[endpoint.get("name")] = endpoint

        # All of the endpoints and services are within the requests_v1 object
        return _TestDescription(
            version=SKYRAMP_YAML_VERSION,
            test={
                "testPattern": [{"startAt": scenario.start_at, "scenarioName": scenario.name}],
            },
            scenarios=[{"name": scenario.name, "steps": steps}],
            services=list(service_dict.values()),
            requests=list(request_dict.values()),
            endpoints=list(endpoint_dict.values()),
            )

    def deploy_target(
        self,
        target_description_path: str,
        namespace: str,
        worker_image: str,
        local_image: bool,
    ) -> None:
        """
        Helps to deploy a target

        Args:
            target_description_path: The path of the target description
            namespace: The namespace where the target will be deployed
            worker_image: The image of the worker
            local_image: Whether the image is local
        """
        func = _library.deployTargetWrapper
        arg_types = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool]
        restype = ctypes.c_char_p

        _call_function(
            func,
            arg_types,
            restype,
            [
                target_description_path.encode(),
                namespace.encode(),
                worker_image.encode(),
                local_image,
            ],
        )

    def delete_target(self, target_description_path: str, namespace: str) -> None:
        """
        this function is used to delete a target

        Args:
            target_description_path: The path of the target description
            namespace: The namespace where the target will be deployed
        """
        func = _library.deleteTargetWrapper
        arg_types = [ctypes.c_char_p, ctypes.c_char_p]
        restype = ctypes.c_char_p

        _call_function(
            func,
            arg_types,
            restype,
            [
                target_description_path.encode(),
                namespace.encode(),
            ]
        )
