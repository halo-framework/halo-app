from __future__ import print_function
import abc
import logging
import uuid
import datetime
# halo
from halo_app.classes import AbsBaseClass
from halo_app.app.context import HaloContext
from halo_app.settingsx import settingsx

logger = logging.getLogger(__name__)

settings = settingsx()

class AbsHaloExchange(AbsBaseClass, abc.ABC):
    id = None
    timestamp = None

    @abc.abstractmethod
    def __init__(self):
        self.id = uuid.uuid4().__str__()
        self.timestamp = datetime.datetime.now().timestamp()