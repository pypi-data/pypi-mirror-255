import json

from faas.system import MetricsLogger, WallClock

from galileofaas.connections import RedisClient


class GalileoLogger(MetricsLogger):

    def __init__(self, rds: RedisClient, clock=None, channel: str = 'galileo/events'):
        self.rds = rds
        self.clock = clock or WallClock()
        self.channel = channel

    def _now(self):
        return self.clock.now()

    def log(self, metric, value, time=None, **tags):
        if time is None:
            time = self._now()
        if type(value) == dict:
            fields = value
        else:
            fields = {
                'value': value
            }
        msg_value = tags | fields
        rds_msg = f'{time} {metric} {json.dumps(msg_value)}'
        self.rds.publish_async(self.channel, rds_msg)
