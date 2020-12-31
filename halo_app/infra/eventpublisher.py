import json
import logging
from dataclasses import asdict
import redis

from halo_app import config
from halo_app.classes import AbsBaseClass
from halo_app.domain.event import AbsHaloEvent

logger = logging.getLogger(__name__)

publisher = None

class Publisher(AbsBaseClass):
    def publish(channel, event: AbsHaloEvent):
        logging.info('publishing: channel=%s, event=%s', channel, event)
        publisher.publish(channel, json.dumps(asdict(event)))
