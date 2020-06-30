from __future__ import print_function

import datetime
import hashlib
import logging
from abc import ABCMeta


from halo_flask.classes import AbsBaseClass
from halo_flask.logs import log_json
from halo_flask.const import SYSTEMChoice,LOGChoice
from .settingsx import settingsx

settings = settingsx()

logger = logging.getLogger(__name__)

ver = settings.DB_VER
read_uri = settings.DB_READ_URL
write_uri = settings.DB_WRITE_URL
tbl = False
page_size = settings.PAGE_SIZE


class AbsDbMixin(AbsBaseClass):
    __metaclass__ = ABCMeta
    # intercept db calls

    halo_context = None
    read = None
    uri = None

    def __init__(self, halo_context,read):
        self.halo_context = halo_context
        self.read = read
        if read:
            self.uri = read_uri
        else:
            self.uri = write_uri
        logger.info("uri:"+str(self.uri))

    def __getattribute__(self, name):
        attr = object.__getattribute__(self, name)
        if hasattr(attr, '__call__'):
            def newfunc(*args, **kwargs):
                now = datetime.datetime.now()
                result = attr(*args, **kwargs)
                total = datetime.datetime.now() - now
                logger.info(LOGChoice.performance_data.value, extra=log_json(self.halo_context,
                                                               {LOGChoice.type.value: SYSTEMChoice.dbaccess.value,
                                                           LOGChoice.milliseconds.value: int(total.total_seconds() * 1000),
                                                           LOGChoice.function.value: str(attr.__name__)}))
                return result

            return newfunc
        else:
            return attr


class AbsModel(AbsBaseClass):
    pass