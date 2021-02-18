from __future__ import print_function

# python
import abc
import datetime
import logging
import traceback
from abc import ABCMeta,abstractmethod
# app
from .utilx import Util
from ..const import SYSTEMChoice, LOGChoice
from ..logs import log_json
from ..reflect import Reflect
from halo_app.app.request import AbsHaloRequest, HaloCommandRequest
from ..classes import AbsBaseClass
from ..settingsx import settingsx

settings = settingsx()
# aws
# other

# Create your view here.
logger = logging.getLogger(__name__)


class GlobalService():

    data_map = None

    def __init__(self, data_map):
        self.data_map = data_map

    @abstractmethod
    def load_global_data(self):
        pass

def load_global_data(class_name,data_map):
    clazz = Reflect.instantiate(class_name, GlobalService, data_map)
    clazz.load_global_data()
