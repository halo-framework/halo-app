from __future__ import print_function

# python
import abc
import datetime
import logging
import os
import traceback
from abc import ABCMeta,abstractmethod
import importlib
import jwt
# app
from ..command import HaloQuery, HaloCommand
from ..exceptions import HaloError
from .utilx import Util
from ..const import HTTPChoice, SYSTEMChoice, LOGChoice, OPType
from ..logs import log_json
from ..reflect import Reflect
from ..request import HaloRequest, HaloCommandRequest, HaloQueryRequest
from ..response import HaloResponse
from ..classes import AbsBaseClass
from ..context import HaloContext
from ..settingsx import settingsx

from halo_app.const import HTTPChoice

settings = settingsx()
# aws
# other

# Create your views here.
logger = logging.getLogger(__name__)

class AbsBoundaryService(AbsBaseClass,abc.ABC):
    """
    the only port exposed from the boundry
    """
    @abc.abstractmethod
    def do_process(self, halo_request: HaloRequest)->HaloResponse:
        pass

class BoundaryService(AbsBoundaryService,abc.ABC):
    __metaclass__ = ABCMeta

    """
        the only point of communication with left-side driver
        adapters. It accepts commands, and calls the appropriate command handler.

        Requires token authentication.
        Only admin users are able to access this view.
        """

    def __init__(self, **kwargs):
        super(BoundaryService, self).__init__(**kwargs)

    def do_process(self,halo_request: HaloRequest)->HaloResponse:
        """

        :param vars:
        :return:
        """
        now = datetime.datetime.now()
        error_message = None
        error = None
        orig_log_level = 0
        http_status_code = 500

        try:
            ret = self.process(halo_request)
            total = datetime.datetime.now() - now
            logger.info(LOGChoice.performance_data.value, extra=log_json(halo_request.context,
                                                                         {LOGChoice.type.value: SYSTEMChoice.server.value,
                                                            LOGChoice.milliseconds.value: int(total.total_seconds() * 1000)}))
            return ret

        except HaloError as e:
            http_status_code = e.status_code
            error = e
            error_message = str(error)
            # @todo check if stack needed and working
            e.stack = traceback.format_exc()
            logger.error(error_message, extra=log_json(halo_request.context, halo_request.args, e))
            # exc_type, exc_obj, exc_tb = sys.exc_info()
            # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            # logger.debug('An error occured in '+str(fname)+' lineno: '+str(exc_tb.tb_lineno)+' exc_type '+str(exc_type)+' '+e.message)

        except Exception as e:
            error = e
            error_message = str(error)
            #@todo check if stack needed and working
            e.stack = traceback.format_exc()
            logger.error(error_message, extra=log_json(halo_request.context, halo_request.args, e))
            # exc_type, exc_obj, exc_tb = sys.exc_info()
            # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            # logger.debug('An error occured in '+str(fname)+' lineno: '+str(exc_tb.tb_lineno)+' exc_type '+str(exc_type)+' '+e.message)

        finally:
            self.process_finally(halo_request.context,orig_log_level)

        total = datetime.datetime.now() - now
        logger.info(LOGChoice.error_performance_data.value, extra=log_json(halo_request.context,
                                                                           {LOGChoice.type.value: SYSTEMChoice.server.value,
                                                              LOGChoice.milliseconds.value: int(total.total_seconds() * 1000)}))

        json_error = Util.json_error_response(halo_request.context, halo_request.args,settings.ERR_MSG_CLASS, error)
        return self.do_abort(halo_request,http_status_code, errors=json_error)

    def do_abort(self,halo_request,http_status_code, errors):
        ret = HaloResponse(halo_request)
        ret.payload = errors
        ret.code = http_status_code
        ret.headers = {}
        return ret

    def process_finally(self,halo_context, orig_log_level):
        """

        :param orig_log_level:
        """
        if Util.isDebugEnabled(halo_context):
            if logger.getEffectiveLevel() != orig_log_level:
                logger.setLevel(orig_log_level)
                logger.debug("process_finally - back to orig:" + str(orig_log_level),
                             extra=log_json(halo_context))

    def process(self,halo_request:HaloRequest)->HaloResponse:
        if isinstance(halo_request,HaloCommandRequest):
            return self.run_command(halo_request)
        return self.run_query(halo_request)



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
