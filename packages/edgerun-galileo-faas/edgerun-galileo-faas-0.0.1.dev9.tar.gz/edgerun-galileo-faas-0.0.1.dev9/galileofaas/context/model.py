from dataclasses import dataclass

from faas.context import PlatformContext, NetworkService, NodeService, ZoneService
from telemc import TelemetryController

from galileofaas.connections import RedisClient
from galileofaas.context.platform.deployment.k8s import KubernetesDeploymentService
from galileofaas.context.platform.replica.factory import KubernetesFunctionReplicaFactory
from galileofaas.context.platform.replica.k8s import KubernetesFunctionReplicaService
from galileofaas.context.platform.telemetry.rds import RedisTelemetryService
from galileofaas.context.platform.trace.rds import RedisTraceService
from galileofaas.system.core import KubernetesFunctionNode


@dataclass
class GalileoFaasContext(PlatformContext):
    deployment_service: KubernetesDeploymentService
    network_service: NetworkService
    node_service: NodeService[KubernetesFunctionNode]
    replica_service: KubernetesFunctionReplicaService
    telemetry_service: RedisTelemetryService
    trace_service: RedisTraceService
    zone_service: ZoneService
    replica_factory: KubernetesFunctionReplicaFactory
    rds: RedisClient
    telemc: TelemetryController
