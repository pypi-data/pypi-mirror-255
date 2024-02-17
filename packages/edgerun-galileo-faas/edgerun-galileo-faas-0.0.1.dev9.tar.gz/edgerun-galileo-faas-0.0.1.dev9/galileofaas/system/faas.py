import logging
import time
from typing import Union, List, Dict, Optional

from faas.system import FaasSystem, FunctionRequest, FunctionContainer, FunctionReplica, FunctionReplicaState

from galileofaas.context.model import GalileoFaasContext
from galileofaas.system.core import GalileoFaasMetrics, KubernetesFunctionDeployment, \
    KubernetesFunctionReplica

logger = logging.getLogger(__name__)


class GalileoFaasSystem(FaasSystem):

    def __init__(self, context: GalileoFaasContext, metrics: GalileoFaasMetrics):
        self.context = context
        self.metrics = metrics

    def deploy(self, fn: KubernetesFunctionDeployment):
        """
        Adds the given deployment to the system and deploys the minimum amount of replicas configured in the
        ScalingConfiguration.
        Note, that the ReplicaService will create a NodeSelector based on the labels of the created Replica.
        In the case of this method, this will inevitably default to the labels configured in the FunctionDeployment and
        FunctionContainer (whereas labels of the FunctionContainer overwrite those in the FunctionDeployment).
        That means the initial Pods of a FunctionDeployment will be placed according to the origina labels of the
        Deployment and Container
        """
        if self.context.deployment_service.exists(fn.name):
            raise ValueError(f'function {fn.name} already deployed')
        logger.info(f'Add FunctionDeployment {fn.name}')
        min_replica = fn.scaling_configuration.scale_min
        replicas = []

        for i in range(min_replica):
            replica = self.context.replica_factory.create_replica(
                labels={},
                fn_container=fn.deployment_ranking.get_first(),
                fn_deployment=fn,
            )
            replicas.append(replica)

        for replica in replicas:
            self.context.replica_service.add_function_replica(replica)

        self.context.deployment_service.add(fn)

    def remove(self, function_name: str):
        if not self.context.deployment_service.exists(function_name):
            logger.info(f'{function_name} not deployed, no removal happening.')
        logger.info(f'Remove FunctionDeployment {function_name}')
        self.context.deployment_service.remove(function_name)

    def invoke(self, request: Union[FunctionRequest]):
        raise NotImplementedError('Use galileo-experiments project to invoke deployed functions')

    def get_deployments(self) -> List[KubernetesFunctionDeployment]:
        return self.context.deployment_service.get_deployments()

    def get_function_index(self) -> Dict[str, FunctionContainer]:
        deployments = self.get_deployments()
        index = {}
        for deployment in deployments:
            for container in deployment.fn_containers:
                index[container.image] = container
        return index

    def get_replicas(self, fn_name: str, running: bool = True, state=None) -> List[FunctionReplica]:
        return self.context.replica_service.get_function_replicas_of_deployment(fn_name, running, state)

    def scale_down(self, function_name: str, remove: Union[int, List[FunctionReplica]]) -> List[FunctionReplica]:
        return self.context.replica_service.scale_down(function_name, remove)

    def scale_up(self, function_name: str, replicas: Union[int, List[FunctionReplica]]) -> List[FunctionReplica]:
        return self.context.replica_service.scale_up(function_name, replicas)

    def discover(self, function: FunctionContainer, running: bool = True, state: FunctionReplicaState = None) -> List[
        FunctionReplica]:
        def predicate(x: KubernetesFunctionReplica) -> bool:
            return x.image == function.image

        return self.context.replica_service.find_by_predicate(predicate, running, state)

    def poll_available_replica(self, fn: str, interval=0.5, timeout: int = None) -> Optional[List[FunctionReplica]]:
        start = time.time()
        while True:
            replicas = self.get_replicas(fn, running=True)
            if len(replicas) > 0:
                return replicas
            if time.time() - start > timeout:
                return None
            time.sleep(interval)
