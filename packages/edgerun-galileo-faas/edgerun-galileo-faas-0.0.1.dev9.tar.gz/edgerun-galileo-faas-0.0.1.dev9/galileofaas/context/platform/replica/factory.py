import os
import uuid
from typing import Dict

from faas.context import NodeService, FunctionDeploymentService, InMemoryFunctionReplicaService, FunctionReplicaFactory
from faas.system import FunctionContainer, FunctionReplica, FunctionReplicaState
from kubernetes import client

from galileofaas.connections import RedisClient
from galileofaas.context.platform.pod.factory import PodFactory
from galileofaas.context.platform.replica.k8s import KubernetesFunctionReplicaService
from galileofaas.system.core import KubernetesFunctionReplica, KubernetesFunctionNode, KubernetesFunctionDeployment, \
    GalileoFaasMetrics


class KubernetesFunctionReplicaFactory(FunctionReplicaFactory[KubernetesFunctionDeployment, KubernetesFunctionReplica]):

    def create_replica(self, labels: Dict[str, str], fn_container: FunctionContainer,
                       fn_deployment: KubernetesFunctionDeployment) -> KubernetesFunctionReplica:
        image = fn_container.fn_image.image.split('/')[1].split(':')[0]
        uid = uuid.uuid4()
        replica_id = f'{image}-{uid}'
        replica = FunctionReplica(
            replica_id,
            labels,
            fn_deployment,
            fn_container,
            None,
            FunctionReplicaState.CONCEIVED
        )
        return KubernetesFunctionReplica(
            replica,
            None,
            None,
            None,
            fn_deployment.namespace,
            None,
            None,
            None,
            replica_id,
            None
        )


def create_replica_service(node_service: NodeService[KubernetesFunctionNode], rds_client: RedisClient,
                           deployment_service: FunctionDeploymentService[KubernetesFunctionDeployment],
                           core_v1_api: client.CoreV1Api, pod_factory: PodFactory,
                           replica_factory: KubernetesFunctionReplicaFactory, metrics: GalileoFaasMetrics
                           ) -> \
        KubernetesFunctionReplicaService:
    replica_service = InMemoryFunctionReplicaService[KubernetesFunctionReplica](node_service, deployment_service,
                                                                                replica_factory)
    async_pod = os.environ.get('galileo_faas_async_pod') == 'True'
    return KubernetesFunctionReplicaService(replica_service, rds_client, node_service, deployment_service, core_v1_api,
                                            pod_factory, async_pod, metrics)
