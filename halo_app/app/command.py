from __future__ import print_function
import abc
import logging
import uuid
# halo
from halo_app.classes import AbsBaseClass
from halo_app.app.context import HaloContext
from halo_app.app.message import AbsHaloMessage
from halo_app.settingsx import settingsx

logger = logging.getLogger(__name__)

settings = settingsx()

class AbsHaloCommand(AbsHaloMessage):
    context = None
    name = None
    vars = None
    version = None
    aggregate_id = None
    aggregate_name = None
    aggregate_revision = None

    def __init__(self):
        super(AbsHaloCommand,self).__init__()


class HaloCommand(AbsHaloCommand):

    def __init__(self, context:HaloContext,name:str,vars:dict):
        super(HaloCommand,self).__init__()
        self.context = context
        self.name = name
        self.vars = vars







