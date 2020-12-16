from __future__ import print_function
import abc
import importlib
import jwt
import logging
import datetime
import uuid
# halo
from halo_app.classes import AbsBaseClass
from halo_app.context import HaloContext
from halo_app.settingsx import settingsx

logger = logging.getLogger(__name__)

settings = settingsx()

class AbsHaloCommandQuery(AbsBaseClass,abc.ABC):
    id = None
    context = None
    name = None
    vars = None

    def __init__(self,id:str):
        self.id = id


class HaloCommand(AbsHaloCommandQuery):

    def __init__(self, context:HaloContext,name:str,vars:dict,id:str=None):
        if not id:
            self.id = uuid.uuid4().__str__()
        super(HaloCommand,self).__init__(id)
        self.context = context
        self.name = name
        self.vars = vars


class HaloQuery(AbsHaloCommandQuery):

    def __init__(self, context:HaloContext,name:str,vars:dict,id:str=None):
        if not id:
            self.id = uuid.uuid4().__str__()
        super(HaloQuery,self).__init__(id)
        self.context = context
        self.name = name
        self.vars = vars





