from __future__ import print_function

# python
import datetime
import logging
import os
import traceback
from abc import ABCMeta,abstractmethod
import importlib
import jwt
# app

from ..exceptions import HaloError
from .utilx import Util
from ..const import HTTPChoice,SYSTEMChoice,LOGChoice
from ..logs import log_json
from ..reflect import Reflect
from ..request import HaloRequest
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

#@todo add jsonify to all responses

class AbsBaseLinkX(AbsBaseClass):
    __metaclass__ = ABCMeta

    """
        View to list all users in the system.

        * Requires token authentication.
        * Only admin users are able to access this view.
        """

    def __init__(self, **kwargs):
        super(AbsBaseLinkX, self).__init__(**kwargs)

    def do_process(self,args=None):
        """

        :param request:
        :param typer:
        :param vars:
        :return:
        """
        now = datetime.datetime.now()
        self.halo_context = HaloContext()
        error_message = None
        error = None
        orig_log_level = 0
        http_status_code = 500

        try:
            ret = self.process(args)
            total = datetime.datetime.now() - now
            logger.info(LOGChoice.performance_data.value, extra=log_json(self.halo_context,
                                                                         {LOGChoice.type.value: SYSTEMChoice.server.value,
                                                            LOGChoice.milliseconds.value: int(total.total_seconds() * 1000)}))
            return ret

        except HaloError as e:
            http_status_code = e.status_code
            error = e
            error_message = str(error)
            # @todo check if stack needed and working
            e.stack = traceback.format_exc()
            logger.error(error_message, extra=log_json(self.halo_context, args, e))
            # exc_type, exc_obj, exc_tb = sys.exc_info()
            # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            # logger.debug('An error occured in '+str(fname)+' lineno: '+str(exc_tb.tb_lineno)+' exc_type '+str(exc_type)+' '+e.message)

        except Exception as e:
            error = e
            error_message = str(error)
            #@todo check if stack needed and working
            e.stack = traceback.format_exc()
            logger.error(error_message, extra=log_json(self.halo_context, args, e))
            # exc_type, exc_obj, exc_tb = sys.exc_info()
            # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            # logger.debug('An error occured in '+str(fname)+' lineno: '+str(exc_tb.tb_lineno)+' exc_type '+str(exc_type)+' '+e.message)

        finally:
            self.process_finally(orig_log_level)

        total = datetime.datetime.now() - now
        logger.info(LOGChoice.error_performance_data.value, extra=log_json(self.halo_context,
                                                                           {LOGChoice.type.value: SYSTEMChoice.server.value,
                                                              LOGChoice.milliseconds.value: int(total.total_seconds() * 1000)}))

        json_error = Util.json_error_response(self.halo_context, args,settings.ERR_MSG_CLASS, error)
        return self.do_abort(http_status_code, errors=json_error)

    def do_abort(self,http_status_code, errors):
        ret = HaloResponse(HaloRequest())
        ret.payload = errors
        ret.code = http_status_code
        ret.headers = {}
        return ret

    def process_finally(self, orig_log_level):
        """

        :param request:
        :param orig_log_level:
        """
        if Util.isDebugEnabled(self.halo_context):
            if logger.getEffectiveLevel() != orig_log_level:
                logger.setLevel(orig_log_level)
                logger.debug("process_finally - back to orig:" + str(orig_log_level),
                             extra=log_json(self.halo_context))



    def get_client_ip(self, request):
        """

        :param request:
        :return:
        """
        ip = request.headers.get('REMOTE_ADDR')
        logger.debug("get_client_ip: " + str(ip), extra=log_json(self.halo_context))
        return ip

    def get_jwt(self, request):
        """

        :param request:
        :return:
        """
        ip = self.get_client_ip(request)
        encoded_token = jwt.encode({'ip': ip}, settings.SECRET_JWT_KEY, algorithm='HS256')
        return encoded_token

    def check_jwt(self, request):  # return true if token matches
        """

        :param request:
        :return:
        """
        ip = self.get_client_ip(request)
        encoded_token = request.GET.get('jwt', None)
        if not encoded_token:
            return False
        decoded_token = jwt.decode(encoded_token, settings.SECRET_JWT_KEY, algorithm='HS256')
        return ip == decoded_token['ip']

    def get_jwt_str(self, request):
        """

        :param request:
        :return:
        """
        return '&jwt=' + self.get_jwt(request).decode()



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

############################################
from .mixinx import AbsApiMixinX
from flask.views import MethodView
from flask import Response
import json
class TestMixinX(AbsApiMixinX,MethodView):
    def get(self):
        ret = self.do_process()
        print(str(ret.payload))
        if ret.code >= 300:
            return Response(ret.payload, status=ret.code, headers=ret.headers)
        return Response(json.dumps(ret.payload), status=ret.code, headers=ret.headers)

    def do_operation_11(self, halo_request):  # basic maturity - single request
        logger.debug("do_operation_1")
        self.now = datetime.datetime.now()
        # 1. get api definition to access the BANK API  - url + vars dict
        back_json = {"msg": str(datetime.datetime.now())+' test page - timing for process: ' + str(datetime.datetime.now() - self.now) + " " + settings.VERSION}
        dict = {'1': back_json}
        # 8. return json response
        return dict

class TestLinkX(TestMixinX, AbsBaseLinkX):
    pass