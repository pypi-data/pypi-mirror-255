from typing import List

from faas.context import InMemoryDeploymentService

from galileofaas.context.platform.deployment.k8s import KubernetesDeploymentService
from galileofaas.system.core import KubernetesFunctionDeployment, GalileoFaasMetrics


def create_deployment_service(metrics: GalileoFaasMetrics,
                              initial_deployments: List[KubernetesFunctionDeployment] = None):
    if initial_deployments is None:
        initial_deployments = []
    in_memory_deployment_service = InMemoryDeploymentService[KubernetesFunctionDeployment](initial_deployments)
    return KubernetesDeploymentService(in_memory_deployment_service, metrics)
