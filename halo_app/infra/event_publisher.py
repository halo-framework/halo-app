import json
import logging
from dataclasses import asdict
import abc
from halo_app.app.command import AbsHaloCommand
from halo_app.classes import AbsBaseClass
from halo_app.app.event import AbsHaloEvent
from halo_app.settingsx import settingsx

logger = logging.getLogger(__name__)

settings = settingsx()


class AbsPublisher(AbsBaseClass,abc.ABC):

    @abc.abstractmethod
    def __init__(self):
        self.publisher = None

    def publish(self,channel, event: AbsHaloEvent):
        logging.info('publishing: channel=%s, event=%s', channel, event)
        self.publisher.publish(channel, json.dumps(asdict(event)))

    def send(self,channel, command: AbsHaloCommand):
        logging.info('publishing: channel=%s, event=%s', channel, command)
        self.publisher.publish(channel, json.dumps(asdict(command)))
