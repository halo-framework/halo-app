import json
import logging
from dataclasses import asdict
import redis

from halo_app.app.command import AbsHaloCommand
from halo_app.classes import AbsBaseClass
from halo_app.app.event import AbsHaloEvent
from halo_app.infra.event_publisher import AbsPublisher
from halo_app.settingsx import settingsx

logger = logging.getLogger(__name__)

settings = settingsx()

class Publisher(AbsPublisher):
    def __init__(self):
        super(Publisher, self).__init__()
        self.publisher = redis.Redis(settings.REDIS_URI)