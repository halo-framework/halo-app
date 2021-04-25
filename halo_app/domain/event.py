from __future__ import annotations
import abc
import logging
import uuid
from dataclasses import dataclass
# halo
from halo_app.app.event import AbsHaloEvent
from halo_app.classes import AbsBaseClass
from halo_app.app.context import HaloContext
from halo_app.app.message import AbsHaloMessage
from halo_app.settingsx import settingsx

logger = logging.getLogger(__name__)

settings = settingsx()


class AbsHaloDomainEvent(AbsHaloEvent):
    agg_root_id = None
    def __init__(self, context: HaloContext, name: str,agg_root_id:str):
        super(AbsHaloEvent, self).__init__(context,name)
        self.agg_root_id = agg_root_id


# concre events are data classes as opose to commands