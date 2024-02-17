import logging
from dataclasses import dataclass
from typing import List, Dict, Optional

from faas.system import ScalingConfiguration, ResourceConfiguration, FunctionNode, FunctionReplica, FunctionDeployment, \
    Metrics
from skippy.core.model import ResourceRequirements

logger = logging.getLogger(__name__)


class KubernetesResourceConfiguration(ResourceConfiguration):
    requests: ResourceRequirements
    limits: Optional[ResourceRequirements]

    def __init__(self, requests: ResourceRequirements = None, limits: ResourceRequirements = None):
        self.requests = requests if requests is not None else ResourceRequirements()
        self.limits = limits

    def get_resource_requirements(self) -> Dict:
        return {
            'cpu': self.requests.requests['cpu'],
            'memory': self.requests.requests['memory']
        }

    def get_resource_limits(self) -> Optional[Dict]:
        if self.limits is not None:
            data = {}
            cpu = self.limits.requests.get('cpu', None)
            memory = self.limits.requests.get('memory', None)
            if cpu is not None:
                data['cpu'] = cpu
            if memory is not None:
                data['memory'] = memory
            return data
        else:
            return None

    @staticmethod
    def create_from_str(cpu: str, memory: str):
        return KubernetesResourceConfiguration(ResourceRequirements.from_str(memory, cpu))


class KubernetesFunctionNode(FunctionNode):
    boot: int
    net: List[str]
    disk: List[str]

    def __init__(self, fn_node: FunctionNode, boot: int, net: List[str], disk: List[str]):
        super().__init__(fn_node.name, fn_node.arch, fn_node.cpus, fn_node.ram, fn_node.netspeed, fn_node.labels,
                         fn_node.allocatable,
                         fn_node.cluster, fn_node.state)
        self.boot = boot
        self.net = net
        self.disk = disk


class KubernetesFunctionReplica(FunctionReplica):
    ip: Optional[str]
    port: Optional[int]
    url: Optional[str]
    namespace: str
    host_ip: Optional[str]
    qos_class: Optional[str]
    start_time: Optional[str]
    # we include also the name of the pod instead of just the pod UID (stored in replica_id)
    pod_name: str
    # we assume that each pod only has one container
    container_id: Optional[str]

    def __init__(self, replica: FunctionReplica, ip: Optional[str], port: Optional[int], url: Optional[str],
                 namespace: str,
                 host_ip: Optional[str],
                 qos_class: Optional[str], start_time: Optional[str], pod_name: str, container_id: Optional[str]):
        super().__init__(replica.replica_id, replica._labels, replica.function, replica.container, replica.node,
                         replica.state)
        self.ip = ip
        self.port = port
        self.url = url
        self.namespace = namespace
        self.host_ip = host_ip
        self.node_name = replica.node.name if replica.node is not None else ''
        self.qos_class = qos_class
        self.start_time = start_time
        self.pod_name = pod_name
        self.container_id = container_id

    def __str__(self):
        return f'KubernetesFunctionReplica {self.replica_id}, {self.state}, {self.pod_name}'

@dataclass
class GalileoFaasScalingConfiguration:
    scaling_config: ScalingConfiguration

    @property
    def scale_min(self):
        return self.scaling_config.scale_min

    @property
    def scale_max(self):
        return self.scaling_config.scale_max

    @property
    def scale_zero(self):
        return self.scaling_config.scale_zero

    @property
    def scale_factor(self):
        return self.scale_factor


@dataclass
class KubernetesFunctionDeployment(FunctionDeployment):
    original_name: str
    namespace: str

    def __init__(self, deployment: FunctionDeployment, original_name: str, namespace: str):
        super(KubernetesFunctionDeployment, self).__init__(deployment.fn, deployment.fn_containers,
                                                           deployment.scaling_configuration,
                                                           deployment.deployment_ranking)
        self.original_name = original_name
        self.namespace = namespace


class GalileoFaasMetrics(Metrics):
    pass
