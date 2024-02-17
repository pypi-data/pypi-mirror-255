from faas.context import NetworkService, NodeService, InMemoryTraceService

from galileofaas.connections import RedisClient
from galileofaas.context.platform.replica.k8s import KubernetesFunctionReplicaService
from galileofaas.context.platform.trace.rds import RedisTraceService
import time

def create_trace_service(window_size: int, rds_client: RedisClient,
                         replica_service: KubernetesFunctionReplicaService,
                         network_service: NetworkService, node_service: NodeService) -> RedisTraceService:
    parser = RedisTraceService.parse_request
    inmemory_service = InMemoryTraceService(lambda: time.time(), window_size, node_service, parser)
    return RedisTraceService(inmemory_service, window_size, rds_client, replica_service, node_service, network_service)
