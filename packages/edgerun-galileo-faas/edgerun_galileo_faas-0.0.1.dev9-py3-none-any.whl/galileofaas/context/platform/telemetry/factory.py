from typing import List, Optional

from faas.context import NodeService

from galileofaas.connections import RedisClient
from galileofaas.context.platform.telemetry.rds import RedisTelemetryService


def create_telemetry_service(window_size: int, rds_client: RedisClient,
                             node_service: NodeService, container_metrics: Optional[List[str]] = None,
                             node_metrics: Optional[List[str]] = None) -> RedisTelemetryService:
    return RedisTelemetryService(window_size, rds_client, node_service, container_metrics=container_metrics,
                                 node_metrics=node_metrics)
