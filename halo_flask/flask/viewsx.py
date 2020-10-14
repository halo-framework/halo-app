from __future__ import print_function

# python
import datetime
import logging
import os
import traceback
from abc import ABCMeta,abstractmethod
import importlib
import jwt
from flask import Response as HttpResponse, abort, render_template,jsonify,redirect
from werkzeug.exceptions import HTTPException
# from flask import request
# flask
from flask.views import MethodView
from ..exceptions import HaloError
from .utilx import Util
from ..const import HTTPChoice,SYSTEMChoice,LOGChoice
from ..logs import log_json
from ..reflect import Reflect
from ..request import HaloRequest
from ..response import HaloResponse
from ..settingsx import settingsx


from ..flask.mixinx import PerfMixinX,TestMixinX,HealthMixinX,InfoMixinX
from flask import request

from halo_flask.const import HTTPChoice

settings = settingsx()
# aws
# other

# Create your views here.
logger = logging.getLogger(__name__)

#@todo add jsonify to all responses

class AbsBaseLinkX(MethodView):
    __metaclass__ = ABCMeta

    """
        View to list all users in the system.

        * Requires token authentication.
        * Only admin users are able to access this view.
        """

    def __init__(self, **kwargs):
        super(AbsBaseLinkX, self).__init__(**kwargs)

    def do_process(self, typer, args=None):
        """

        :param request:
        :param typer:
        :param vars:
        :return:
        """
        now = datetime.datetime.now()
        self.halo_context = Util.get_halo_context(request)
        error_message = None
        error = None
        orig_log_level = 0
        http_status_code = 500

        if Util.isDebugEnabled(self.halo_context, request):
            orig_log_level = logger.getEffectiveLevel()
            logger.setLevel(logging.DEBUG)
            logger.debug("DebugEnabled - in debug mode",
                         extra=log_json(self.halo_context, Util.get_req_params(request)))

        logger.debug("headers", extra=log_json(self.halo_context, Util.get_headers(request)))

        logger.debug("environ", extra=log_json(self.halo_context, os.environ))

        try:
            ret = self.process(request,typer, args)
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
            logger.error(error_message, extra=log_json(self.halo_context, Util.get_req_params(request), e))
            # exc_type, exc_obj, exc_tb = sys.exc_info()
            # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            # logger.debug('An error occured in '+str(fname)+' lineno: '+str(exc_tb.tb_lineno)+' exc_type '+str(exc_type)+' '+e.message)

        except Exception as e:
            error = e
            error_message = str(error)
            #@todo check if stack needed and working
            e.stack = traceback.format_exc()
            logger.error(error_message, extra=log_json(self.halo_context, Util.get_req_params(request), e))
            # exc_type, exc_obj, exc_tb = sys.exc_info()
            # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            # logger.debug('An error occured in '+str(fname)+' lineno: '+str(exc_tb.tb_lineno)+' exc_type '+str(exc_type)+' '+e.message)

        finally:
            self.process_finally(request, orig_log_level)

        total = datetime.datetime.now() - now
        logger.info(LOGChoice.error_performance_data.value, extra=log_json(self.halo_context,
                                                                           {LOGChoice.type.value: SYSTEMChoice.server.value,
                                                              LOGChoice.milliseconds.value: int(total.total_seconds() * 1000)}))

        json_error = Util.json_error_response(self.halo_context,request, settings.ERR_MSG_CLASS, error)
        if settings.FRONT_WEB:
            return redirect("/" + settings.ENV_NAME +"/"+ str(http_status_code))
        self.do_abort(http_status_code, errors=json_error)

    def do_abort(self,http_status_code, **kwargs):
        """Raise a HTTPException for the given http_status_code. Attach any keyword
        arguments to the exception for later processing.
        """
        # noinspection PyUnresolvedReferences
        try:
            abort(http_status_code)
        except HTTPException as e:
            if len(kwargs):
                e.data = kwargs
            raise

    def process_finally(self, request, orig_log_level):
        """

        :param request:
        :param orig_log_level:
        """
        if Util.isDebugEnabled(self.halo_context, request):
            if logger.getEffectiveLevel() != orig_log_level:
                logger.setLevel(orig_log_level)
                logger.debug("process_finally - back to orig:" + str(orig_log_level),
                             extra=log_json(self.halo_context))

    def process(self,request, typer, args):
        """
        Return a list of all users.
        """

        if typer == HTTPChoice.get:
            return self.process_get(request,args)

        if typer == HTTPChoice.post:
            return self.process_post(request,args)

        if typer == HTTPChoice.put:
            return self.process_put(request,args)

        if typer == HTTPChoice.patch:
            return self.process_patch(request,args)

        if typer == HTTPChoice.delete:
            return self.process_delete(request,args)

        return HttpResponse('this is a ' + str(typer) )

    def process_get(self,request, args):
        """

        :param request:
        :param vars:
        :return:
        """
        # return HttpResponse('this is process get on ' + self.get_view_name())
        ret = HaloResponse(HaloRequest(request))
        ret.payload = 'this is process get on '  # + self.get_view_name()
        ret.code = 200
        ret.headers = {}
        return ret

    def process_post(self,request, args):
        """

        :param request:
        :param vars:
        :return:
        """
        # return HttpResponse('this is process post on ' + self.get_view_name())
        ret = HaloResponse(HaloRequest(request))
        ret.payload = 'this is process post on '  # + self.get_view_name()
        ret.code = 201
        ret.headers = {}
        return ret

    def process_put(self,request, args):
        """

        :param request:
        :param vars:
        :return:
        """
        # return HttpResponse('this is process put on ' + self.get_view_name())
        ret = HaloResponse(HaloRequest(request))
        ret.payload = 'this is process put on '  # + self.get_view_name()
        ret.code = 200
        ret.headers = {}
        return ret

    def process_patch(self,request, args):
        """

        :param request:
        :param vars:
        :return:
        """
        # return HttpResponse('this is process patch on ' + self.get_view_name())
        ret = HaloResponse(HaloRequest(request))
        ret.payload = 'this is process patch on '  # + self.get_view_name()
        ret.code = 200
        ret.headers = {}
        return ret

    def process_delete(self,request, args):
        """

        :param request:
        :param vars:
        :return:
        """
        # return HttpResponse('this is process delete on ' + self.get_view_name())
        ret = HaloResponse(HaloRequest(request))
        ret.payload = 'this is process delete on '  # + self.get_view_name()
        ret.code = 200
        ret.headers = {}
        return ret

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

    def get(self):
        ret = self.do_process(HTTPChoice.get,request.args)
        return Util.json_data_response(ret.payload, ret.code, ret.headers)

    def post(self):
        ret = self.do_process(HTTPChoice.post,request.args)
        return Util.json_data_response(ret.payload, ret.code, ret.headers)

    def put(self):
        ret = self.do_process(HTTPChoice.put,request.args)
        return Util.json_data_response(ret.payload, ret.code, ret.headers)

    def patch(self):
        ret = self.do_process(HTTPChoice.patch,request.args)
        return Util.json_data_response(ret.payload, ret.code, ret.headers)

    def delete(self):
        ret = self.do_process(HTTPChoice.delete,request.args)
        return Util.json_data_response(ret.payload, ret.code, ret.headers)


class TestLinkX(TestMixinX, AbsBaseLinkX):
    pass

class PerfLinkX(PerfMixinX, AbsBaseLinkX):
    pass

class HealthLinkX(HealthMixinX, AbsBaseLinkX):
    pass

class InfoLinkX(InfoMixinX, AbsBaseLinkX):
    pass

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

