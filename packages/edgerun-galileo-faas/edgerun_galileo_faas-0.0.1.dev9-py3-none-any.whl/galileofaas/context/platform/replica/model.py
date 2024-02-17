import logging
from copy import copy
from dataclasses import dataclass, field
from typing import Optional, Dict

from dataclasses_json import dataclass_json
from faas.context import FunctionDeploymentService, NodeService
from faas.system import FunctionReplicaState, FunctionContainer, FunctionReplica, FunctionDeployment, FunctionNode, FunctionImage, Function
from faas.util.constant import function_label, pod_not_running, pod_running, pod_unknown, pod_failed, pod_succeeded, \
    pod_pending
from skippy.core.model import ResourceRequirements
from galileofaas.system.core import KubernetesFunctionReplica, KubernetesFunctionNode
from galileofaas.system.core import KubernetesResourceConfiguration, KubernetesFunctionDeployment
from faas.system import FunctionImage, Function, FunctionContainer, FunctionDeployment, ScalingConfiguration, DeploymentRanking
logger = logging.getLogger(__name__)
import json
# Defaults taken from:
# https://github.com/kubernetes/kubernetes/blob/4c659c5342797c9a1f2859f42b2077859c4ba621/pkg/scheduler/util/pod_resources.go#L25
default_milli_cpu_request = '100m'  # 0.1 core
default_mem_request = f'{200}Mi'  # 200 MB


@dataclass_json
@dataclass
class Container:
    id: str
    name: str
    image: str
    port: int
    resource_requests: Dict[str, str]
    resource_limits: Dict[str, str]


@dataclass_json
@dataclass
class Pod:
    podUid: str
    name: str
    namespace: str
    qosClass: str
    labels: Dict[str, str]
    status: str
    startTime: Optional[str] = ""
    podIP: Optional[str] = ""
    nodeName: Optional[str] = ""
    hostIP: Optional[str] = ""
    containers: Optional[Dict[str, Container]] = field(default_factory=dict)


def convert_kubernetes_status(status: str) -> FunctionReplicaState:
    if status == pod_not_running:
        return FunctionReplicaState.SHUTDOWN
    if status == pod_running:
        return FunctionReplicaState.RUNNING
    if status == pod_unknown:
        return FunctionReplicaState.SHUTDOWN
    if status == pod_failed:
        return FunctionReplicaState.SHUTDOWN
    if status == pod_succeeded:
        return FunctionReplicaState.SHUTDOWN
    if status == pod_pending:
        return FunctionReplicaState.PENDING
    raise ValueError(f'Unknown status {status}')



def parse_function_replica(text: str, fn_deployment_service: FunctionDeploymentService,
                           node_service: NodeService[KubernetesFunctionNode]) -> \
        Optional[KubernetesFunctionReplica]:
    try:
        pod = Pod.from_json(text)
    except Exception as e:
        logger.error(e)
        raise e
    ip = None
    container_id = None
    container_image = None
    port = None
    url = None
    node = None

    if len(pod.containers) > 0:
        container = list(pod.containers.values())[0]
        container_id = container.id.replace('containerd://', '')
        container_image = container.image

        port = container.port
        ip = pod.podIP
        url = f'{ip}:{port}'

    labels = copy(pod.labels)
    fn_label_value = labels.get(function_label, None)

    fn_deployment = fn_deployment_service.get_by_name(fn_label_value)

    if fn_deployment is None:
        # logger.info(f'Cant find deployment for {pod.name}')
        return None
    if len(pod.nodeName) > 0:
        node = node_service.find(pod.nodeName)
        if node is None:
            raise ValueError(f'Replica "{pod.name}" runs on unknown node "{pod.nodeName}"')

    fn_container: FunctionContainer = fn_deployment.get_container(container_image)
    fn_replica: FunctionReplica = FunctionReplica(
        replica_id=pod.name,
        labels=labels,
        function=fn_deployment,
        container=fn_container,
        node=node,
        state=convert_kubernetes_status(pod.status)
    )

    k8s_replica = KubernetesFunctionReplica(
        replica=fn_replica,
        ip=ip,
        port=port,
        url=url,
        namespace=pod.namespace,
        host_ip=pod.hostIP,
        qos_class=pod.qosClass,
        start_time=pod.startTime,
        pod_name=pod.name,
        container_id=container_id
    )
    return k8s_replica
