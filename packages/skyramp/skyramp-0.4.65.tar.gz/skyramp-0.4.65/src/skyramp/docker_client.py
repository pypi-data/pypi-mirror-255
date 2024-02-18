""" This class contains methods to manage Docker containers and volumes."""
import ctypes
from skyramp.utils import _library, _call_function
from skyramp.client import _ClientBase

WORKER_URL = "public.ecr.aws/j1n2c2p2/rampup/worker"
WORKER_TAG = "latest"
VOLUME_NAME = "skyramp-worker"
CONTAINER_NAME = "skyramp"
CONTAINER_PORT = 35142
class WorkerInfoType(ctypes.Structure):
    """ c type for worker info"""
    _fields_ = [
        ("container_name", ctypes.c_char_p),
        ("error", ctypes.c_char_p),
    ]
class _DockerClient(_ClientBase):
    """ This class contains methods to manage Docker containers and volumes."""
    def __init__(self, network_name: str=""):
        super().__init__()
        self.network_name = network_name

    def run_container(
            self,
            worker_url: str=WORKER_URL,
            worker_tag: str=WORKER_TAG,
            host_port: int=CONTAINER_PORT,
            ):
        """
        Run a Docker container with the specified configuration.

        Args:
            worker_url (str): URL of the worker image.
            worker_tag (str): Tag of the worker image.
            container_port (int): Port to map to the container.

        Returns:
            docker.models.containers.Container: The running Docker container.
        """
        func = _library.newStartDockerSkyrampWorkerWrapper
        argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p]
        worker_info =WorkerInfoType
        restype = ctypes.POINTER(worker_info)

        output = _call_function(
            func,
            argtypes,
            restype,
            [
                worker_url.encode(),
                worker_tag.encode(),
                host_port,
                self.network_name.encode(),
            ],
            True,
        )
        return output

    def docker_down(self, container_name: str):
        """ Stop and remove the Docker container. """
        func = _library.newDeleteDockerSkyrampWorkerWrapper
        argtypes = [ctypes.c_char_p]
        restype = ctypes.c_char_p

        err = _call_function(
            func,
            argtypes,
            restype,
            [container_name.encode()],
        )
        if err:
            raise Exception(err)
