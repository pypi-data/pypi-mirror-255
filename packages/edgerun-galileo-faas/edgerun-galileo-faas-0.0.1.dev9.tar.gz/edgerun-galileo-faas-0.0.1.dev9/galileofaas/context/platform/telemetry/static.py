import datetime
from typing import Optional, Dict

import pandas as pd
from faas.context import TelemetryService, FunctionReplicaService, NodeService

from galileofaas.context.platform.telemetry import util
from galileofaas.util.telemetry import Resources


class StaticTelemetryService(TelemetryService):

    def __init__(self, replica_service: FunctionReplicaService, node_service: NodeService,
                 container_resources: Dict[str, Resources],
                 node_resources: Dict[str, Resources]):
        self.replica_service = replica_service
        self.node_service = node_service
        self.container_resources = container_resources
        self.node_resources = node_resources

    def get_replica_cpu(self, replica_id: str, start: datetime.datetime = None, end: datetime.datetime = None) -> \
            Optional[pd.DataFrame]:
        pod = self.replica_service.get_function_replica_by_id(replica_id)
        if pod is None:
            return None
        else:
            node = pod.node
            cores = node.cpus
            return util.get_replica_cpu(self.container_resources, replica_id, cores, start, end)

    def get_node_cpu(self, node: str, start: datetime.datetime = None, end: datetime.datetime = None) -> Optional[pd.DataFrame]:
        df = util.get_node_cpu(self.node_resources, node)
        df = df['ts'] >= start
        df = df['ts'] <= end
        return df



