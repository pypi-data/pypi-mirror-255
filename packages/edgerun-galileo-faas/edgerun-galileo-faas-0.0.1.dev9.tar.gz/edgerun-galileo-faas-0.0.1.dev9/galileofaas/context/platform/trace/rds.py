import json
import logging
import re
import threading
import time
from typing import Dict, Optional, Callable
from galileofaas.util.pubsub import POISON

import pandas as pd
from faas.context import TraceService, InMemoryTraceService, NetworkService, NodeService, ResponseRepresentation
from faas.system import FunctionResponse, FunctionRequest, FunctionReplica, FunctionNode
from faas.util.constant import client_role_label, zone_label
from galileodb.model import RequestTrace
from galileodb.recorder.traces import TracesSubscriber

from galileofaas.connections import RedisClient
from galileofaas.context.platform.replica.k8s import KubernetesFunctionReplicaService
from galileofaas.system.core import KubernetesFunctionNode
from galileofaas.util.network import update_latencies

logger = logging.getLogger(__name__)


class RedisTraceService(TraceService):

    def __init__(self, inmemory_trace_service: InMemoryTraceService[FunctionResponse], window_size: int,
                 rds_client: RedisClient,
                 replica_service: KubernetesFunctionReplicaService,
                 node_service: NodeService[KubernetesFunctionNode],
                 network_service: NetworkService):
        self.window_size = window_size
        self.rds_client = rds_client
        self.traces_subscriber = TracesSubscriber(rds_client.conn())
        self.replica_service: KubernetesFunctionReplicaService = replica_service
        self.node_service = node_service
        self.network_service = network_service
        self.inmemory_trace_service = inmemory_trace_service
        self.t = None

    def get_values_for_function(self, function: str, start: float, end: float,
                                access: Callable[['ResponseRepresentation'], float], zone: str = None,
                                response_status: int = None):
        return self.inmemory_trace_service.get_values_for_function(function, start, end, access, zone,
                                                                   response_status)


    def get_values_for_function_by_sent(self, function: str, start: float, end: float,
                                access: Callable[['ResponseRepresentation'], float], zone: str = None,
                                response_status: int = None):
        return self.inmemory_trace_service.get_values_for_function_by_sent(function, start, end, access, zone,
                                                                   response_status)

    def get_traces_for_function(self, function_name: str, start: float, end: float, zone: str = None,
                                response_status: int = None):
        return self.inmemory_trace_service.get_traces_for_function(function_name, start, end, zone,
                                                                   response_status)

    def get_traces_for_function_image(self, function: str, function_image: str, start: float, end: float,
                                      zone: str = None,
                                      response_status: int = None):
        now = time.time()
        return self.inmemory_trace_service.get_traces_for_function_image(function, function_image,
                                                                         start, end, zone,
                                                                         response_status)

    @staticmethod
    def parse_request(req: FunctionResponse) -> Optional[ResponseRepresentation]:
        origin_zone = RedisTraceService._origin_zone(req.client)
        destination_zone = req.replica.labels[zone_label]
        sent = req.ts_start
        done = req.ts_end
        rtt = done - sent
        rep = ResponseRepresentation(
            ts=done,
            function=req.replica.function.name,
            function_image=req.replica.container.fn_image.image,
            replica_id=req.replica.replica_id,
            node=req.replica.node.name,
            rtt=rtt,
            done=done,
            sent=sent,
            origin_zone=origin_zone,
            dest_zone=destination_zone,
            client=req.client,
            status=req.code,
            request_id=req.request_id
        )
        logger.debug(rep)
        return rep

    def get_traces_api_gateway(self, node_name: str, start: float, end: float,
                               response_status: int = None) -> pd.DataFrame:
        return self.inmemory_trace_service.get_traces_api_gateway(node_name, start, end,
                                                                  response_status)

    def find_node_for_client(self, client: str) -> Optional[KubernetesFunctionNode]:
        nodes = self.replica_service.find_function_replicas_with_labels(node_labels={client_role_label: "true"})
        for replica in nodes:
            if replica.pod_name in client:
                node = self.node_service.find(replica.node_name)
                return node
        return None

    def run(self):
        for trace in self.traces_subscriber.run():
            if trace == POISON:
                return
            logger.debug("Got trace %s", trace)
            if trace.status == -1:
                logger.info("Failed trace received!")
                continue
            headers = json.loads(trace.headers)
            final_host = headers.get('X-Final-Host', '').split(',')[-1].split(':')[0].replace(' ', '')
            # running=False will look for all pods with the given IP
            replica = self.replica_service.get_function_replica_with_ip(final_host, running=False)
            if replica is None:
                logger.warning(f"Looked up non-existent pod ip {final_host}")
                continue
            node = self.node_service.find(replica.node_name)
            client_node = self.find_node_for_client(trace.client)
            # logger.info(f'client_node: {client_node}')
            self.update_latencies(client_node.name, trace.sent, headers)
            # logger.info('updated latencies')
            if node is None:
                logger.error("GalileoFaasNode was None when looking for the serving pod %s", replica.node_name)
                logger.debug("all nodes stored currently %s", str([x.name for x in self.node_service.get_nodes()]))
                continue
            function_response: FunctionResponse = self._parse_galileo_trace(trace, node, replica)

            self.add_trace(function_response)

    @staticmethod
    def _origin_zone(client: str) -> Optional[str]:
        # TODO use context node service to find node and read zone from label
        galileo_worker_zone_pattern = "zone-.{1}"
        try:
            return re.search(galileo_worker_zone_pattern, client).group(0)
        except (AttributeError, IndexError):
            logger.warning(f"can't find zone pattern in client {client}")
            return None

    def _parse_galileo_trace(self, trace: RequestTrace, node: FunctionNode,
                             replica: FunctionReplica) -> FunctionResponse:
        function_request = FunctionRequest(
            name=replica.fn_name,
            start=trace.sent,
            # TODO add size to trace
            size=0,
            request_id=trace.request_id,
            # add body to trace?
            body='',
            client=trace.client,
            replica=None,
            headers=trace.headers
        )

        ts_wait = -1
        ts_exec = trace.sent
        fet = trace.done - trace.sent
        if trace.headers is not None:
            try:
                headers = json.loads(trace.headers)
                ts_exec = float(headers.get('X-Start', 0))
                ts_end_fet = float(headers.get('X-End', 0))
                fet = ts_end_fet - ts_exec
            except Exception as e:
                logger.error(e)

        return FunctionResponse(
            request=function_request,
            request_id=trace.request_id,
            client=trace.client,
            name=replica.fn_name,
            body='',
            size=0,
            code=trace.status,
            ts_start=trace.sent,
            ts_wait=ts_wait,
            ts_exec=ts_exec,
            ts_end=trace.done,
            fet=fet,
            replica=replica,
            node=node
        )

    def add_trace(self, response: FunctionResponse):
        self.inmemory_trace_service.add_trace(response)

    def start(self):
        logger.info('Start RedisTraceService subscription thread')
        self.t = threading.Thread(target=self.run)
        self.t.start()
        return self.t

    def stop(self, timeout: float = 5):
        self.traces_subscriber.close()
        if self.t is not None:
            self.t.join(timeout)
        logger.info('Stopped RedisTraceService subscription thread')

    def update_latencies(self, client_node: str, sent: float, headers: Dict[str, str]):
        """
        Updates the latencies based on the data in headers.
        First reads X-Forwarded-For to get all nodes in the request trace, and then updates the latency between each node.
        Starting with the client-gateway connection.
        """

        updates = update_latencies(client_node, sent, headers, self.replica_service)
        for nodes, latency in updates.items():
            self.network_service.update_latency(nodes[0], nodes[1], latency)
