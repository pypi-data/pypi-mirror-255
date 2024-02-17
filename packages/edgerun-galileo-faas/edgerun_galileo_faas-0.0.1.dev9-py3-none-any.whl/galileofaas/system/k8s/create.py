import logging
from multiprocessing.pool import ApplyResult
from typing import Union

from galileofaas.context.platform.pod.factory import PodFactory
from galileofaas.system.core import KubernetesFunctionReplica

logger = logging.getLogger(__name__)

from kubernetes import client


def create_pod_from_replica(replica: KubernetesFunctionReplica, pod_factory: PodFactory, core_v1_api: client.CoreV1Api,
                            async_pod: bool, **kwargs) -> Union[client.V1Pod, ApplyResult]:
    pod = pod_factory.create_pod(replica, **kwargs)

    return create_pod(core_v1_api, pod, replica.namespace, async_pod)


def create_pod(v1: client.CoreV1Api, pod: client.V1Pod, namespace: str = 'default',
               async_req: bool = False) -> Union[client.V1Pod, ApplyResult]:
    """
    Creates a Pod in the given namespace
    """
    logger.info(f"Create pod '{pod.metadata.name}'")
    return v1.create_namespaced_pod(namespace, pod, async_req=async_req)
