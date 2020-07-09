from __future__ import print_function

import json
# python
import logging
import re
import os
import uuid
import random
import importlib
from flask import Response
from ..settingsx import settingsx
from halo_flask.classes import AbsBaseClass
from halo_flask.const import HTTPChoice,LOC
from halo_flask.request import HaloContext
from halo_flask.exceptions import ApiTimeOutExpired, CacheError, HaloException, ProviderError
from halo_flask.providers.providers import get_provider,ONPREM
from halo_flask.exceptions import NoCorrelationIdException

settings = settingsx()

logger = logging.getLogger(__name__)


def strx(str1):
    """

    :param str1:
    :return:
    """
    if str1:
        try:
            return str1.encode('utf-8').strip()
        except AttributeError as e:
            return str(str1)
        except Exception as e:
            return str(str1)
    return ''

class Util(AbsBaseClass):

    @staticmethod
    def get_header_name(request,header):
        provider = get_provider()
        if provider:
            header_name = provider.get_header_name(request,header)
        else:
            header_name = header
        return header_name

    @staticmethod
    def get_chrome_browser(cls,request):
        """

        :param request:
        :return:
        """
        header_name = cls.get_header_name(request, HaloContext.items[HaloContext.USER_AGENT])
        CHROME_AGENT_RE = re.compile(r".*(Chrome)", re.IGNORECASE)
        NON_CHROME_AGENT_RE = re.compile(
            r".*(Aviator | ChromePlus | coc_ | Dragon | Edge | Flock | Iron | Kinza | Maxthon | MxNitro | Nichrome | OPR | Perk | Rockmelt | Seznam | Sleipnir | Spark | UBrowser | Vivaldi | WebExplorer | YaBrowser)",
            re.IGNORECASE)
        if CHROME_AGENT_RE.match(request.headers[header_name]):
            if NON_CHROME_AGENT_RE.match(request.headers[header_name]):
                return False
            else:
                return True
        else:
            return False

    @staticmethod
    def mobile(cls,request):
        """Return True if the request comes from a mobile device.
        :param request:
        :return:
        """
        header_name = cls.get_header_name(request, HaloContext.items[HaloContext.USER_AGENT])
        MOBILE_AGENT_RE = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)
        if MOBILE_AGENT_RE.match(request.headers[header_name]):
            return True
        else:
            return False

    @classmethod
    def get_correlation_id(cls, request):
        """

        :param request:
        :return:
        """
        header_name = cls.get_header_name(request, HaloContext.items[HaloContext.CORRELATION])
        if header_name in request.headers:
            return request.headers[header_name]
        else:
            provider = get_provider()
            if provider:
                return provider.get_request_id(request)
        raise NoCorrelationIdException("")

    @classmethod
    def get_user_agent(cls, request):
        """

        :param request:
        :return:
        """
        header_name = cls.get_header_name(request, HaloContext.items[HaloContext.USER_AGENT])
        if header_name in request.headers:
            user_agent = request.headers[header_name]
        else:
            user_agent = cls.get_func_name() + ':' + request.path + ':' + request.method + ':' + settings.INSTANCE_ID
        return user_agent

    @classmethod
    def get_debug_enabled(cls, request):
        """

        :param request:
        :return:
        """
        # check if the specific call is debug enabled
        header_name = cls.get_header_name(request, HaloContext.items[HaloContext.DEBUG_LOG])
        if header_name in request.headers:
            dlog = request.headers[header_name]
            if dlog == 'true':
                return 'true'
        # check if system wide enabled - done on edge
        header_name = cls.get_header_name(request, HaloContext.items[HaloContext.CORRELATION])
        if header_name not in request.headers:
            dlog = cls.get_system_debug_enabled()
            if dlog == 'true':
                return 'true'
        return 'false'

    @staticmethod
    def get_headers(request):
        """

        :param request:
        :return:
        """
        regex_http_ = re.compile(r'^HTTP_.+$')
        regex_content_type = re.compile(r'^CONTENT_TYPE$')
        regex_content_length = re.compile(r'^CONTENT_LENGTH$')
        request_headers = {}
        for header, value in request.headers:
            logger.debug("header=" + str(header))
            if regex_http_.match(header) or regex_content_type.match(header) or regex_content_length.match(header):
                request_headers[header] = value  # request.headers[header]
        return request_headers

    @staticmethod
    def get_client_ip(cls,request):  # front - when browser calls us
        """

        :param request:
        :return:
        """
        header = 'HTTP_X_FORWARDED_FOR'
        header_name = cls.get_header_name(request, header)
        x_forwarded_for = request.headers.get(header_name)
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            header = 'REMOTE_ADDR'
            header_name = cls.get_header_name(request, header)
            ip = request.headers.get(header_name)
        return ip

    @staticmethod
    def get_server_client_ip(cls,request):  # not front - when service calls us
        """

        :param request:
        :return:
        """
        header = 'HTTP_REFERER'
        header_name = cls.get_header_name(request, header)
        return request.headers.get(header_name)



    """"
    Success
    response
    return data
    {
        "data": {
            "id": 1001,
            "name": "Wing"
        }
    }
    Error
    response
    return error
    {
        "error": {
            "code": 404,
            "message": "ID not found",
            "requestId": "123-456"
        }
    }
    """

    @staticmethod
    def json_data_response(data, status_code=200, headers={}):
        """

        :param data:
        :param status_code:
        :return:
        """
        if status_code >= 300:
            return Response(data, status=status_code, headers=headers)
        return Response(json.dumps(data), status=status_code, headers=headers)
        #return jsonify(data)

    @staticmethod
    def get_req_params(request):
        """

        :param request:
        :return:
        """
        qd = {}
        if request.method == HTTPChoice.get.value:
            qd = request.args
        elif request.method == HTTPChoice.post.value:
            qd = request.args
        return qd

    @classmethod
    def get_timeout(cls, request):
        """

        :param request:
        :return:
        """
        provider = get_provider()
        if provider.PROVIDER_NAME != ONPREM:
            timeout =  provider.get_timeout(request)
            if timeout:
                return timeout
        return settings.SERVICE_CONNECT_TIMEOUT_IN_SC

    @classmethod
    def get_halo_context(cls, request, api_key=None):
        """
        :param request:
        :param api_key:
        :return:
        """
        x_correlation_id = cls.get_correlation_id(request)
        x_user_agent = cls.get_user_agent(request)
        dlog = cls.get_debug_enabled(request)
        ret = {HaloContext.items[HaloContext.USER_AGENT]: x_user_agent, HaloContext.items[HaloContext.REQUEST]: cls.get_request_id(request),
               HaloContext.items[HaloContext.CORRELATION]: x_correlation_id, HaloContext.items[HaloContext.DEBUG_LOG]: dlog}
        if api_key:
            ret[HaloContext.items[HaloContext.API_KEY]] = api_key
        ctx = HaloContext(request)
        ctx.dict = ret
        return ctx

    @staticmethod
    def get_func_name():
        """

        :return:
        """
        provider = get_provider()
        if provider.PROVIDER_NAME != ONPREM:
            return provider.get_func_name()
        return settings.FUNC_NAME

    @staticmethod
    def get_func_ver():
        """

        :return:
        """
        provider = get_provider()
        if provider.PROVIDER_NAME != ONPREM:
            return provider.get_func_ver()
        return settings.FUNC_VER

    @staticmethod
    def get_func_region():
        """

        :return:
        """
        provider = get_provider()
        if provider.PROVIDER_NAME != ONPREM:
            return provider.get_func_region()
        raise ProviderError("no region defined")

    @classmethod
    def get_request_id(cls,request):
        provider = get_provider()
        if provider:
            return provider.get_request_id(request)
        raise ProviderError("no provider defined")

    @classmethod
    def get_system_debug_enabled(cls):
        """

        :return:
        """
        # check if env var for sampled debug logs is on and activate for percentage in settings (5%)
        if ('DEBUG_LOG' in os.environ and os.environ['DEBUG_LOG'] == 'true') or (cls.get_debug_param() == 'true'):
            rand = random.random()
            if settings.LOG_SAMPLE_RATE > rand:
                return 'true'
        return 'false'

    @staticmethod
    def get_debug_param():
        """

        :return:
        """
        # check if env var for sampled debug logs is on and activate for percentage in settings (5%)
        dbg = 'false'
        if settings.SSM_CONFIG is None:
            return dbg
        try:
            DEBUG_LOG = settings.SSM_CONFIG.get_param('DEBUG_LOG')
            dbg = DEBUG_LOG["val"]
            logger.debug("get_debug_param=" + dbg)
        except CacheError as e:
            pass
        return dbg

    @classmethod
    def isDebugEnabled(cls, halo_context, request=None):
        """

        :param req_context:
        :param request:
        :return:
        """
        # disable debug logging by default, but allow override via env variables
        # or if enabled via forwarded request context or if debug flag is on
        if halo_context.get(
                HaloContext.items[HaloContext.DEBUG_LOG]) == 'true' or cls.get_system_debug_enabled() == 'true':
            return True
        return False

    @staticmethod
    def json_error_response(halo_context,request, clazz, e):  # code, msg, requestId):
        """

        :param req_context:
        :param clazz:
        :param e:
        :return:
        """
        module = importlib.import_module(clazz)
        my_class = getattr(module, 'ErrorMessages')
        msgs = my_class()
        error_code, message = msgs.get_code(e)
        error_detail = ""
        e_msg = ""
        if hasattr(e, 'detail'):
            error_detail = e.detail
        elif hasattr(e, 'original_exception'):
            error_detail = str(e.original_exception)
        else:
            if hasattr(e, 'message'):
                e_msg = e.message
            else:
                e_msg = str(e)
            if e_msg is not None and e_msg != 'None' and e_msg != "":
                error_detail = e_msg
        error_data = {}
        if hasattr(e, 'data'):
            error_data = json.dumps(e.data)
        payload = {"error":
                       {"error_code": error_code, "error_message": message, "error_detail": error_detail,
                             "data": error_data, "trace_id": halo_context.get(HaloContext.items[HaloContext.CORRELATION])}
                   }
        if Util.isDebugEnabled(halo_context) and hasattr(e, 'stack'):
            payload["stack"] = json.dumps(e.stack)
            payload["request"] = json.dumps(Util.get_req_params(request))
        return payload