from __future__ import annotations
import abc
import logging
import uuid
from typing import List, Dict, Callable, Type, TYPE_CHECKING
from dataclasses import dataclass
# halo
from halo_app.classes import AbsBaseClass
from halo_app.app.context import HaloContext
from halo_app.app.message import AbsHaloMessage
from halo_app.settingsx import settingsx

logger = logging.getLogger(__name__)

settings = settingsx()

@dataclass
class AbsHaloCommand(AbsHaloMessage,abc.ABC):
    name = None
    vars = None

    @abc.abstractmethod
    def __init__(self):
        super(AbsHaloCommand,self).__init__()


class HaloCommand(AbsHaloCommand):

    def __init__(self, name:str,vars:Dict):
        super(HaloCommand,self).__init__()
        self.name = name
        self.vars = vars







