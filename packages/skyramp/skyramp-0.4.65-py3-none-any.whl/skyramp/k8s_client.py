"""
Skyramp client object which can be used to interact with a k8s cluster.
"""
import ctypes
from skyramp.utils import _library, _call_function
from skyramp.client import _ClientBase

class _K8SClient(_ClientBase):
    """
    Skyramp client object which can be used to interact with a k8s cluster.
    """
    def __init__(
        self,
        kubeconfig_path: str = "",
        cluster_name: str = "",
        context: str = "",
    ) -> None:
        """
        Initializes a Skyramp Client.

        Args:
            kubeconfig_path: The filesystem path of a kubeconfig
            cluster_name: The name of the cluster.
            context: The Kubernetes context within a kubeconfig
        """
        super().__init__()
        self.kubeconfig_path = kubeconfig_path
        self.cluster_name = cluster_name
        self.context = context
        self.project_path = ""
        self._namespace_set = set()
        self.global_headers = {}

    def apply_local(self) -> None:
        """
        Creates a local cluster.
        """
        apply_local_function = _library.applyLocalWrapper
        argtypes = []
        restype = ctypes.c_char_p

        _call_function(apply_local_function, argtypes, restype, [])

        self.kubeconfig_path = self._get_kubeconfig_path()
        if not self.kubeconfig_path:
            raise Exception("no kubeconfig found")

    def remove_local(self) -> None:
        """
        Removes a local cluster.
        """
        func = _library.removeLocalWrapper
        argtypes = []
        restype = ctypes.c_char_p

        _call_function(func, argtypes, restype, [])

    def add_kubeconfig(
        self,
        context: str,
        cluster_name: str,
        kubeconfig_path: str,
    ) -> None:
        """
        Adds a preexisting Kubeconfig file to Skyramp.

        Args:
            context: The kubeconfig context to use
            cluster_name: Name of the cluster
            kubeconfig_path: filepath of the kubeconfig
        """
        func = _library.addKubeconfigWrapper
        argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
        restype = ctypes.c_char_p

        _call_function(
            func,
            argtypes,
            restype,
            [
                context.encode(),
                cluster_name.encode(),
                kubeconfig_path.encode(),
            ],
        )

        self.kubeconfig_path = kubeconfig_path

    def remove_cluster(self, cluster_name: str) -> None:
        """
        Removes a cluster, corresponding to the name, from Skyramp
        """
        func = _library.removeClusterFromConfigWrapper
        argtypes = [ctypes.c_char_p]
        restype = ctypes.c_char_p

        _call_function(func, argtypes, restype, [cluster_name.encode()])

    def deploy_skyramp_worker(
        self, namespace: str, worker_image: str='', local_image: bool=False
    ) -> None:
        """
        Installs a Skyramp worker onto a cluster if one is registered with Skyramp

        Args:
            namespace: The namespace to deploy the worker to
            worker_image: The image of the worker
            local_image: Whether the image is local(default- False)
        """
        if not self.kubeconfig_path:
            raise Exception("no cluster to deploy worker to")
        func = _library.deploySkyrampWorkerWrapper
        argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool]
        restype = ctypes.c_char_p

        _call_function(
            func,
            argtypes,
            restype,
            [namespace.encode(), worker_image.encode(), local_image],
        )

        self._namespace_set.add(namespace)

    def delete_skyramp_worker(self, namespace: str) -> None:
        """
        Removes the Skyramp worker, if a Skyramp worker is installed on a registered Skyramp cluster

        Args:
            namespace: The namespace to delete the worker from
        """
        if not self.kubeconfig_path:
            raise Exception("no cluster to delete worker from")

        if namespace not in self._namespace_set:
            raise Exception(f"no worker to delete from {namespace} namespace")

        func = _library.deleteSkyrampWorkerWrapper
        argtypes = [ctypes.c_char_p]
        restype = ctypes.c_char_p

        _call_function(func, argtypes, restype, [namespace.encode()])

        self._namespace_set.remove(namespace)

    def _get_kubeconfig_path(self) -> str:
        func = _library.getKubeConfigPath
        argtypes = []
        restype = ctypes.c_char_p

        return _call_function(func, argtypes, restype, [], True)


class _Client(_K8SClient):
    """ 
    Deprecated: Skyramp client object which can be used to interact with a k8s cluster.
    Use `K8SClient` class instead.
    """
