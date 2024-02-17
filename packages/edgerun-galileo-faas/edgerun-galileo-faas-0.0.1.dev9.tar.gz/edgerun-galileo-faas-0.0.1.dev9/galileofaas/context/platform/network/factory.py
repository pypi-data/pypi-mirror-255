from typing import Tuple, Dict

from faas.context import NetworkService
from faas.context.platform.network.inmemory import InMemoryNetworkService


def create_network_service(min_latency: float, max_latency: float,
                           latency_map: Dict[Tuple[str, str], float]) -> NetworkService:
    return InMemoryNetworkService(min_latency, max_latency, latency_map)
