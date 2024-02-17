import datetime
import logging
import threading
from typing import Dict, Optional, List

import pandas as pd
from faas.context import TelemetryService, NodeService
from faas.util.point import Point

from galileofaas.connections import RedisClient
from galileofaas.context.platform.telemetry import util
from galileofaas.util.pubsub import POISON
from galileofaas.util.telemetry import Resources

logger = logging.getLogger(__name__)


def parse_channel(event):
    channel = event['channel']
    split_channel = channel.split('/')
    node = split_channel[1]
    metric = split_channel[2]
    return metric, node, split_channel


def parse_data(event):
    msg = event['data']
    split = msg.split(' ', maxsplit=2)
    ts = float(split[0])
    val = float(split[1])
    return msg, ts, val


class RedisTelemetryService(TelemetryService):
    # key is container id
    container_resources: Dict[str, Resources]

    # key is node name
    node_resources: Dict[str, Resources]

    def __init__(self, window_size: int, rds_client: RedisClient, node_service: NodeService, channel='telem/*',
                 container_metrics: List[str] = None, node_metrics: List[str] = None):
        self.window_size = window_size
        self.node_service = node_service
        self.rds_client = rds_client
        self.t: threading.Thread = None
        if container_metrics is None:
            self._container_metrics = ["kubernetes_cgrp_cpu", "kubernetes_cgrp_mem", "kubernetes_cgrp_blkio"]
        else:
            self._container_metrics = container_metrics

        if node_metrics is None:
            self._node_metrics = ["cpu", "ram", "load"]
        else:
            self._node_metrics = node_metrics

        self.container_resources = {}
        self.node_resources = {}
        self.channel = channel

    def get_replica_cpu(self, replica_id: str, start: datetime.datetime = None, end: datetime.datetime = None) -> \
            Optional[pd.DataFrame]:
        resources = self.container_resources.get(replica_id, None)
        if resources is None:
            return None
        cores = self.node_service.find(resources.node).cpus
        return util.get_replica_cpu(self.container_resources, replica_id, cores, start, end)

    def get_node_cpu(self, node: str, start: datetime.datetime = None, end: datetime.datetime = None):
        df = util.get_node_cpu(self.node_resources, node)
        if start is not None:
            df = df[df['ts'] >= start]
        if end is not None:
            df = df[df['ts'] <= end]
        return df

    def get_node_resource(self, node: str, resource: str, start: datetime.datetime = None,
                          end: datetime.datetime = None) -> Optional[pd.DataFrame]:
        """
        Returns dataframe for given resource.
        Dataframe has the following columns and is sorted by timestamp ascending:
        node, ts, value
        """
        df = util.get_node_resources(self.node_resources, node, resource)
        if df is None or len(df) == 0:
            return None
        if start is not None:
            df = df[df['ts'] >= start]
        if end is not None:
            df = df[df['ts'] <= end]
        return df

    def get_replica_resource(self, replica_id: str, resource: str, start: datetime.datetime = None,
                             end: datetime.datetime = None) -> Optional[pd.DataFrame]:
        """
        Returns dataframe for given resource.
        Dataframe has the following columns and is sorted by timestamp ascending:
        replica_id, node, ts, value
        """
        df = util.get_replica_resources(self.container_resources, replica_id, resource)
        if start is not None:
            df = df[df['ts'] >= start]
        if end is not None:
            df = df[df['ts'] <= end]
        return df

    def get_node_ram(self, node: str):
        return util.get_node_ram(self.node_resources,node)

    def save_container_metric(self, node: str, metric: str, container_id: str, ts: float, val: float):
        resources = self.container_resources.get(container_id, None)
        if resources is None:
            self.container_resources[container_id] = Resources(node, self.window_size, self._container_metrics)
            resources = self.container_resources[container_id]

        window = Point(ts=ts, val=val)
        resources.append(metric, window)

    def save_node_metric(self, node: str, metric: str, ts: float, val: float):
        resources = self.node_resources.get(node, None)
        if resources is None:
            self.node_resources[node] = Resources(node, self.window_size, self._node_metrics)
            resources = self.node_resources[node]

        window = Point(ts=ts, val=val)
        resources.append(metric, window)

    def run(self):
        for event in self.rds_client.psub(self.channel):
            if event['data'] == POISON:
                break
            # logger.debug("got event", event)
            # channel parsing
            metric, node, split_channel = parse_channel(event)

            # data parsing
            msg, ts, val = parse_data(event)

            if len(split_channel) == 4 and metric != 'rd' and metric != 'wr' and metric != 'rx' and metric != 'tx':
                # resource with subsystem
                # TODO differentiate between container as subsystem and host related metrics (i.e., rd) and subsystem
                container_id = split_channel[3]
                self.save_container_metric(node, metric, container_id, ts, val)

            elif len(split_channel) == 3:
                # node resource
                self.save_node_metric(node, metric, ts, val)

    def start(self):
        logger.info('Start RedisTelemetryService subscription thread')
        self.t = threading.Thread(target=self.run)
        self.t.start()
        return self.t

    def stop(self, timeout: float = 5):
        self.rds_client.close()
        if self.t is not None:
            self.t.join(timeout)
        logger.info('Stopped RedisTelemetryService subscription thread')
