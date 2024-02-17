import logging

from galileofaas.context.model import GalileoFaasContext
from galileofaas.util.pubsub import POISON
from galileodb.reporter.traces import RedisTraceReporter

logger = logging.getLogger(__name__)


class GalileoFaasContextDaemon:

    def __init__(self, context: GalileoFaasContext):
        self.context = context
        self.telemetry_thread = None
        self.trace_thread = None
        self.replica_thread = None

    def run(self):
        self.telemetry_thread = self.context.telemetry_service.start()
        self.trace_thread = self.context.trace_service.start()
        self.replica_thread = self.context.replica_service.start()
        pass

    def start(self):
        self.run()

    def stop(self, timeout=5):
        logger.info("Stop GalileoFaasContextDaemon thread")
        self.context.rds.publish_async(self.context.replica_service.channel, POISON)
        self.context.rds.publish_async(self.context.telemetry_service.channel, POISON)
        self.context.rds.publish_async(RedisTraceReporter.channel, POISON)

        for t in [self.context.telemetry_service, self.context.trace_service, self.context.replica_service]:
            t.stop(timeout)

        logger.info("Stopped GalileoFaasContextDaemon thread")
