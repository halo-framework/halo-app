from __future__ import print_function

# python
import datetime
import importlib
import logging
import time
from abc import ABCMeta,abstractmethod

import requests
import json
from .exceptions import MaxTryHttpException, ApiError



logger = logging.getLogger(__name__)



class AbsBaseClass(object):
    __metaclass__ = ABCMeta

    @classmethod
    def version(self):
        return "1.0"

    @abstractmethod
    def show(self):
        raise NotImplementedError

    def toJSON(self):
        #return json.dumps(self, default=lambda o: o.__dict__,
        #                  sort_keys=True, indent=4)
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()
            if isinstance(o, datetime.date):
                serial = o.isoformat()
                return serial
            if isinstance(o, datetime.time):
                serial = o.isoformat()
                return serial

        return json.dumps(self.__dict__, default = myconverter)




