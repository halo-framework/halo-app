from __future__ import annotations
import abc
import logging
import uuid
from dataclasses import dataclass
# halo
from halo_app.classes import AbsBaseClass
from halo_app.app.context import HaloContext
from halo_app.app.message import AbsHaloMessage
from halo_app.settingsx import settingsx

logger = logging.getLogger(__name__)

settings = settingsx()

@dataclass
class AbsHaloEvent(AbsHaloMessage,abc.ABC):
    context = None
    name = None

    @abc.abstractmethod
    def __init__(self, context:HaloContext,name:str):
        super(AbsHaloEvent, self).__init__()
        self.context = context
        self.name = name



# concre events are data classes as opose to commands