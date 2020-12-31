from __future__ import print_function
import abc
import logging
import uuid
# halo
from halo_app.classes import AbsBaseClass
from halo_app.app.context import HaloContext
from halo_app.domain.message import AbsHaloMessage
from halo_app.settingsx import settingsx

logger = logging.getLogger(__name__)

settings = settingsx()

class AbsHaloCommand(AbsHaloMessage):
    context = None
    name = None
    vars = None

    def __init__(self):
        super(AbsHaloCommand,self).__init__()


class HaloCommand(AbsHaloCommand):

    def __init__(self, context:HaloContext,name:str,vars:dict):
        super(HaloCommand,self).__init__()
        self.context = context
        self.name = name
        self.vars = vars







