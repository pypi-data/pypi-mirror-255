import json
import logging
import os
import threading
from typing import Dict, List, Optional, Callable, Union
import time
from faas.context import InMemoryFunctionReplicaService, FunctionReplicaService, NodeService, FunctionDeploymentService
from faas.context.observer.api import Observer
from faas.system import FunctionReplicaState
from faas.system.exception import FunctionReplicaCreationException
from faas.util.constant import hostname_label, zone_label
from kubernetes import client
from kubernetes.client import ApiException

from galileofaas.connections import RedisClient
from galileofaas.context.platform.pod.factory import PodFactory
from galileofaas.context.platform.replica.model import parse_function_replica
from galileofaas.system.core import KubernetesFunctionReplica, KubernetesFunctionNode, KubernetesFunctionDeployment, \
    GalileoFaasMetrics
from galileofaas.system.k8s.create import create_pod_from_replica
from galileofaas.system.k8s.delete import delete_pod
from galileofaas.util.pubsub import POISON
from concurrent.futures import ThreadPoolExecutor
logger = logging.getLogger(__name__)


class KubernetesFunctionReplicaService(FunctionReplicaService[KubernetesFunctionReplica]):
    """
    This implementation of the FunctionReplicaService uses internally a InMemoryFunctionReplicaService
    that manages the in-memory state.
    Further, it modifies the connected Kubernetes cluster (i.e., add_function_replica will create a corresponding Pod
    in the cluster).
    It does however keep, as mentioned already, an in-memory state - which means that Kubernetes is never invoked
    to retrieve any pods.
    This implementation offers the ability to run as daemon and listen for events published via Redis.
    Specifically listens on events emitted from the telemd-kubernetes-adapter.
    """


    def __init__(self, replica_service: InMemoryFunctionReplicaService[KubernetesFunctionReplica],
                 rds_client: RedisClient,
                 node_service: NodeService[KubernetesFunctionNode],
                 deployment_service: FunctionDeploymentService[KubernetesFunctionDeployment],
                 core_v1_api: client.CoreV1Api,
                 pod_factory: PodFactory,
                 async_pod: bool,
                 metrics: GalileoFaasMetrics,
                 channel='galileo/events'):
        super().__init__()
        self.replica_service = replica_service
        self.node_service = node_service
        self.deployment_service = deployment_service
        self.rds_client = rds_client
        self.channel = channel
        self.core_v1_api = core_v1_api
        self.pod_factory = pod_factory
        self.async_pod = async_pod
        self.metrics = metrics
        self.t = None
        self.delete_executor = ThreadPoolExecutor(max_workers=10)
        # in seconds
        self.delete_delay = float(os.getenv('DELETE_DELAY', 3))

    def get_function_replica_with_ip(self, ip: str, running: bool = True, state: FunctionReplicaState = None) -> \
            Optional[
                KubernetesFunctionReplica]:

        def predicate(replica: KubernetesFunctionReplica) -> bool:
            return replica.ip == ip

        replicas = self.replica_service.find_by_predicate(predicate, running, state)
        if len(replicas) == 0:
            return None
        else:
            return replicas[0]

    def get_function_replicas(self) -> List[KubernetesFunctionReplica]:
        return self.replica_service.get_function_replicas()

    def get_function_replicas_of_deployment(self, fn_deployment_name, running: bool = True,
                                            state: FunctionReplicaState = None) -> List[
        KubernetesFunctionReplica]:
        return self.replica_service.get_function_replicas_of_deployment(fn_deployment_name, running, state)

    def find_function_replicas_with_labels(self, labels: Dict[str, str] = None, node_labels=None, running: bool = True,
                                           state: str = None) -> List[
        KubernetesFunctionReplica]:
        return self.replica_service.find_function_replicas_with_labels(labels, node_labels, running, state)

    def get_function_replica_by_id(self, replica_id: str) -> Optional[KubernetesFunctionReplica]:
        return self.replica_service.get_function_replica_by_id(replica_id)

    def get_function_replica_with_id(self, replica_id: str) -> Optional[KubernetesFunctionReplica]:
        return self.replica_service.get_function_replica_with_id(replica_id)

    def get_function_replicas_on_node(self, node_name: str) -> List[KubernetesFunctionReplica]:
        return self.replica_service.get_function_replicas_on_node(node_name)

    def _marshal_replica(self ,replica: KubernetesFunctionReplica):
        obj = {
            'podUid': replica.replica_id,
            'containers': {
                replica.container_id: {
                    'id': replica.container_id,
                    'name': replica.pod_name,
                    'image': replica.container.image,
                    'resource_requests': replica.container.get_resource_requirements(),
                    'resource_limits': replica.container.get_resource_requirements(),
                    'port': replica.port
                }
            },
            'namespace': replica.namespace,
            'hostIP': replica.host_ip,
            'name': replica.pod_name,
            'podIP': replica.ip,
            'qosClass': replica.qos_class,
            'startTime': replica.start_time,
            'labels': replica.labels,
            'status': 'Not Running',
            'nodeName': replica.node_name
        }
        return obj

    def _publish_shutdown_event(self, replica: KubernetesFunctionReplica):
        ts = time.time()
        event = 'pod/shutdown'
        channel = 'galileo/events'
        json_obj = self._marshal_replica(replica)
        msg = f'{ts} {event} {json_obj}'
        self.metrics.logger.log(event, json_obj, ts)

    def delayed_shutdown_function_replica(self, replica_id: str):
        logger.info(f'Start delayed shutdown {replica_id}')
        replica = self.replica_service.get_function_replica_by_id(replica_id)
        self._publish_shutdown_event(replica)
        self.replica_service.shutdown_function_replica(replica_id)
        def _delete():
            logger.info(f'Delete replica in {self.delete_delay} seconds...')
            time.sleep(self.delete_delay)
            self.delete_now(replica)

        self.delete_executor.submit(lambda: _delete())

    def delete_now(self, replica):
        logger.info(f'Delete now {replica}')
        delete_pod(self.core_v1_api, replica.pod_name, replica.namespace, self.async_pod)

    def shutdown_function_replica(self, replica_id: str):
        replica = self.replica_service.get_function_replica_by_id(replica_id)
        self.replica_service.shutdown_function_replica(replica_id)
        # delete_pod(self.core_v1_api, replica.pod_name, replica.namespace, self.async_pod)

    def delete_function_replica(self, replica_id: str):
        self.replica_service.delete_function_replica(replica_id)

    def find_by_predicate(self, predicate: Callable[[KubernetesFunctionReplica], bool], running: bool = True,
                          state: FunctionReplicaState = None) -> \
            List[KubernetesFunctionReplica]:
        return self.replica_service.find_by_predicate(predicate, running, state)

    def add_function_replica(self, replica: KubernetesFunctionReplica) -> KubernetesFunctionReplica:
        # this boolean is needed to decide below whether to actually deploy the replica or if it was merely a status update
        is_conceived = replica.state == FunctionReplicaState.CONCEIVED
        exists = self.replica_service.get_function_replica_by_id(replica.replica_id) == None
        self.metrics.log_function_replica(replica)
        self.replica_service.add_function_replica(replica)

        if is_conceived and not exists:
            try:
                node_selector = {}
                if replica.labels.get(zone_label, None) is not None:
                    node_selector[zone_label] = replica.labels[zone_label]
                if replica.labels.get(hostname_label, None) is not None:
                    node_selector[hostname_label] = replica.labels[hostname_label]
                # TODO handle async return value (i.e., error)
                create_pod_from_replica(replica, self.pod_factory, self.core_v1_api, self.async_pod,
                                        node_selector=node_selector)
                return replica
            except ApiException:
                raise FunctionReplicaCreationException()

    def scale_down(self, function_name: str, remove: Union[int, List[KubernetesFunctionReplica]]):
        removed = self.replica_service.scale_down(function_name, remove)
        for removed_replica in removed:
            self.delayed_shutdown_function_replica(removed_replica.replica_id)
        self.metrics.log_scaling(function_name, len(removed))
        return removed

    def scale_up(self, function_name: str, add: Union[int, List[KubernetesFunctionReplica]]) -> List[
        KubernetesFunctionReplica]:
        added = self.replica_service.scale_up(function_name, add)
        for added_replica in added:
            self.add_function_replica(added_replica)
        self.metrics.log_scaling(function_name, len(added))
        return added

    def run(self):
        for event in self.rds_client.sub(self.channel):
            try:
                if event['data'] == POISON:
                    break
                msg = event['data']
                # logger.info("Got message: %s", msg)
                split = msg.split(' ', maxsplit=2)
                event = split[1]
                if 'pod' in event:
                    try:
                        # logger.info(split[2])
                        replica = parse_function_replica(split[2], self.deployment_service, self.node_service)
                        if replica is None:
                            # ignore this was triggered most likely because the pod did adhere to our function replica structure
                            logger.warning(f"Emitted pod was ignored: {split[2]}")
                            pass
                        else:
                            logger.debug(f"Handler container event ({event}):  {replica.replica_id}")
                            if event == 'pod/running':
                                self.metrics.log_replica_lifecycle(replica, FunctionReplicaState.RUNNING)
                                logger.debug(f"Set pod running: {replica.replica_id}")
                                self.add_function_replica(replica)
                            elif event == 'pod/delete':
                                self.metrics.log_replica_lifecycle(replica, FunctionReplicaState.DELETE)
                                logger.debug(f'Delete pod {replica.replica_id}')
                                self.delete_function_replica(replica.replica_id)
                            elif event == 'pod/create':
                                logger.debug(f"create pod: {replica.replica_id}")
                                self.metrics.log_replica_lifecycle(replica, FunctionReplicaState.CONCEIVED)
                                self.add_function_replica(replica)
                            elif event == 'pod/pending':
                                self.metrics.log_replica_lifecycle(replica, FunctionReplicaState.PENDING)
                                logger.info(f"pending pod: {replica.replica_id}")
                                self.add_function_replica(replica)
                            elif event == 'pod/shutdown':
                                self.metrics.log_replica_lifecycle(replica, FunctionReplicaState.SHUTDOWN)
                                logger.debug(f"shutdown pod {replica.replica_id}")
                                self.shutdown_function_replica(replica.replica_id)
                            else:
                                logger.error(f'unknown pod event ({event}): {replica.replica_id}')
                    except Exception as e:
                        # logger.error(f"error parsing container - {msg}")
                        pass
                elif event == 'scale_schedule':
                    # TODO this might need update
                    obj = json.loads(split[2])
                    if obj['delete'] is True:
                        name = obj['pod']['pod_name']
                        replica = self.get_function_replica_by_id(name)
                        logger.info(f'Got scale_schedule event. Delete replica {replica}')
                        self.shutdown_function_replica(replica.replica_id)
                else:
                    # ignore - not of interest
                    pass
            except Exception as e:
                logging.error(e)
            pass

    def start(self):
        logger.info('Start KubernetesFunctionReplicaService subscription thread')
        self.t = threading.Thread(target=self.run)
        self.t.start()
        return self.t

    def stop(self, timeout: float = 5):
        self.rds_client.close()
        if self.t is not None:
            t: threading.Thread = self.t
            t.join(timeout)
        logger.info('Stopped KubernetesFunctionReplicaService subscription thread')

    def register(self, observer: Observer):
        self.replica_service.register(observer)

