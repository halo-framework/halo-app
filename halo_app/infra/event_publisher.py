import json
import logging
from dataclasses import asdict

from halo_app.classes import AbsBaseClass
from halo_app.app.event import AbsHaloEvent
from halo_app.settingsx import settingsx

logger = logging.getLogger(__name__)

settings = settingsx()
logger = logging.getLogger(__name__)

publisher = None#redis.Redis(**config.get_redis_host_and_port())


class Publisher(AbsBaseClass):
    def publish(self,channel, event: AbsHaloEvent):
        logging.info('publishing: channel=%s, event=%s', channel, event)
        publisher.publish(channel, json.dumps(asdict(event)))
