import logging

from faas.context import InMemoryNodeService, NodeService
from telemc import TelemetryController

from galileofaas.context.platform.node import map_node_info_to_node
from galileofaas.system.core import KubernetesFunctionNode

logger = logging.getLogger(__name__)


def create_node_service(telemc: TelemetryController) -> NodeService[KubernetesFunctionNode]:
    node_infos = telemc.get_node_infos()
    nodes = []
    logger.debug(node_infos)
    for node_info in node_infos:
        nodes.append(map_node_info_to_node(node_info))
    zones = set()
    for node in nodes:
        if node.cluster is not None:
            zones.add(node.cluster)
    zones = list(zones)
    return InMemoryNodeService[KubernetesFunctionNode](zones, nodes)
