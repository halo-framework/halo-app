from __future__ import print_function
import abc
import logging
import uuid
# halo
from halo_app.classes import AbsBaseClass
from halo_app.app.context import HaloContext
from halo_app.settingsx import settingsx

logger = logging.getLogger(__name__)

settings = settingsx()


class AbsHaloObject(AbsBaseClass, abc.ABC):
    pass

class AbsHaloValue(AbsHaloObject):
    pass

class AbsHaloEntity(AbsHaloObject):
    id = None
    def __init__(self,id=None):
        super(AbsHaloEntity, self).__init__()
        if not id:
            self.id = uuid.uuid4().__str__()
        else:
            self.id = id

class AbsHaloAggregateRoot (AbsHaloEntity):
    events = []
    def __init__(self,id=None):
        super(AbsHaloAggregateRoot, self).__init__(id)