import json
import logging
from dataclasses import asdict

from halo_app.classes import AbsBaseClass
from halo_app.app.event import AbsHaloEvent
from halo_app.settingsx import settingsx

logger = logging.getLogger(__name__)

settings = settingsx()

publisher = None

class Publisher(AbsBaseClass):
    def publish(channel, event: AbsHaloEvent):
        logging.info('publishing: channel=%s, event=%s', channel, event)
        publisher.publish(channel, json.dumps(asdict(event)))
