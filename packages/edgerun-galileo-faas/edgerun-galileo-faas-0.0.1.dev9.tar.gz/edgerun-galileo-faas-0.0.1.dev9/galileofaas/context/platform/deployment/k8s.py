from typing import List, Optional

from faas.context import FunctionDeploymentService, InMemoryDeploymentService

from galileofaas.system.core import KubernetesFunctionDeployment, GalileoFaasMetrics


class KubernetesDeploymentService(FunctionDeploymentService[KubernetesFunctionDeployment]):

    def __init__(self, in_memory_deployment_service: InMemoryDeploymentService[KubernetesFunctionDeployment],
                 metrics: GalileoFaasMetrics):
        self.metrics = metrics
        self.in_memory_deployment_service: InMemoryDeploymentService[
            KubernetesFunctionDeployment] = in_memory_deployment_service

    def get_deployments(self) -> List[KubernetesFunctionDeployment]:
        return self.in_memory_deployment_service.get_deployments()

    def get_by_name(self, fn_name: str) -> Optional[KubernetesFunctionDeployment]:
        return self.in_memory_deployment_service.get_by_name(fn_name)

    def exists(self, name: str) -> bool:
        return self.in_memory_deployment_service.exists(name)

    def add(self, deployment: KubernetesFunctionDeployment):
        self.metrics.log_function_deployment(deployment)

        self.in_memory_deployment_service.add(deployment)

    def remove(self, function_name: str):
        deployment = self.get_by_name(function_name)
        self.metrics.log_function_deployment_remove(deployment)
        self.in_memory_deployment_service.remove(function_name)
