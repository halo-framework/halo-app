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
from halo_flask.exceptions import ApiTimeOutExpired,CacheError
from halo_flask.providers.providers import get_provider
from halo_flask.exceptions import NoCorrelationIdException

class status(AbsBaseClass):

    def is_informational(code):
        return 100 <= code <= 199

    def is_success(code):
        return 200 <= code <= 299

    def is_redirect(code):
        return 300 <= code <= 399

    def is_client_error(code):
        return 400 <= code <= 499

    def is_server_error(code):
        return 500 <= code <= 599

    HTTP_100_CONTINUE = 100
    HTTP_101_SWITCHING_PROTOCOLS = 101
    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_202_ACCEPTED = 202
    HTTP_203_NON_AUTHORITATIVE_INFORMATION = 203
    HTTP_204_NO_CONTENT = 204
    HTTP_205_RESET_CONTENT = 205
    HTTP_206_PARTIAL_CONTENT = 206
    HTTP_207_MULTI_STATUS = 207
    HTTP_300_MULTIPLE_CHOICES = 300
    HTTP_301_MOVED_PERMANENTLY = 301
    HTTP_302_FOUND = 302
    HTTP_303_SEE_OTHER = 303
    HTTP_304_NOT_MODIFIED = 304
    HTTP_305_USE_PROXY = 305
    HTTP_306_RESERVED = 306
    HTTP_307_TEMPORARY_REDIRECT = 307
    HTTP_308_PERMANENT_REDIRECT = 308
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_402_PAYMENT_REQUIRED = 402
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_405_METHOD_NOT_ALLOWED = 405
    HTTP_406_NOT_ACCEPTABLE = 406
    HTTP_407_PROXY_AUTHENTICATION_REQUIRED = 407
    HTTP_408_REQUEST_TIMEOUT = 408
    HTTP_409_CONFLICT = 409
    HTTP_410_GONE = 410
    HTTP_411_LENGTH_REQUIRED = 411
    HTTP_412_PRECONDITION_FAILED = 412
    HTTP_413_REQUEST_ENTITY_TOO_LARGE = 413
    HTTP_414_REQUEST_URI_TOO_LONG = 414
    HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415
    HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE = 416
    HTTP_417_EXPECTATION_FAILED = 417
    HTTP_428_PRECONDITION_REQUIRED = 428
    HTTP_429_TOO_MANY_REQUESTS = 429
    HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE = 431
    HTTP_444_CONNECTION_CLOSED_WITHOUT_RESPONSE = 444
    HTTP_500_INTERNAL_SERVER_ERROR = 500
    HTTP_501_NOT_IMPLEMENTED = 501
    HTTP_502_BAD_GATEWAY = 502
    HTTP_503_SERVICE_UNAVAILABLE = 503
    HTTP_504_GATEWAY_TIMEOUT = 504
    HTTP_505_HTTP_VERSION_NOT_SUPPORTED = 505
    HTTP_508_LOOP_DETECTED = 508
    HTTP_510_NOT_EXTENDED = 510
    HTTP_511_NETWORK_AUTHENTICATION_REQUIRED = 511

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
    def json_data_response(data, status_code=200, headers=[]):
        """

        :param data:
        :param status_code:
        :return:
        """
        if status_code >= 300:
            return Response(data, status=status_code, headers=headers)
        return Response(json.dumps({"data": data}), status=status_code, headers=headers)

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

#########################################################################################33

#@todo clean these methods or move to aws provider

    @staticmethod
    def get_lambda_context(request):
        """

        :param request:
        :return:
        """
        # AWS_REGION
        # AWS_LAMBDA_FUNCTION_NAME
        # 'lambda.context'
        # x-amzn-RequestId
        if 'lambda.context' in request.headers:
            return request.headers['lambda.context']
        elif 'context' in request.headers:
            return request.headers['context']
        else:
            return None

    @staticmethod
    def get_func_name():
        """

        :return:
        """
        if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
            return os.environ['AWS_LAMBDA_FUNCTION_NAME']
        else:
            return settings.FUNC_NAME

    @staticmethod
    def get_func_ver():
        """

        :return:
        """
        if 'AWS_LAMBDA_FUNCTION_VERSION' in os.environ:
            return os.environ['AWS_LAMBDA_FUNCTION_VERSION']
        else:
            return "VER"

    @staticmethod
    def get_func_mem():
        """

        :return:
        """
        if 'AWS_LAMBDA_FUNCTION_MEMORY_SIZE' in os.environ:
            return os.environ['AWS_LAMBDA_FUNCTION_MEMORY_SIZE']
        else:
            return "MEM"

    @staticmethod
    def get_func_region():
        """

        :return:
        """
        if 'AWS_REGION' in os.environ:
            return os.environ['AWS_REGION']
        else:
            if 'AWS_DEFAULT_REGION' in os.environ:
                return os.environ['AWS_DEFAULT_REGION']
            return settings.AWS_REGION



    @classmethod
    def get_context(cls):
        """

        :return:
        """
        ret = {"awsRegion": cls.get_func_region(), "functionName": cls.get_func_name(),
               "functionVersion": cls.get_func_ver(), "functionMemorySize": cls.get_func_mem(),
               "stage": cls.get_stage()}
        return ret

    @classmethod
    def get_timeout(cls, request):
        """

        :param request:
        :return:
        """
        if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
            context = cls.get_lambda_context(request)
            if context:
                return cls.get_timeout_mili(context)
        return settings.SERVICE_CONNECT_TIMEOUT_IN_SC

    @classmethod
    def get_timeout_mili(cls, context):
        """

        :param context:
        :return:
        """
        mili = context.get_remaining_time_in_millis()
        logger.debug("mili=" + str(mili))
        sc = mili / 1000
        timeout = sc - settings.RECOVER_TIMEOUT_IN_SC
        logger.debug("timeout=" + str(timeout))
        if timeout > settings.MINIMUM_SERVICE_TIMEOUT_IN_SC:
            return timeout
        raise ApiTimeOutExpired("left " + str(timeout))

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
        ret = {HaloContext.items[HaloContext.USER_AGENT]: x_user_agent, HaloContext.items[HaloContext.REQUEST]: cls.get_aws_request_id(request),
               HaloContext.items[HaloContext.CORRELATION]: x_correlation_id, HaloContext.items[HaloContext.DEBUG_LOG]: dlog}
        if api_key:
            ret[HaloContext.items[HaloContext.API_KEY]] = api_key
        ctx = HaloContext(request)
        ctx.dict = ret
        return ctx

    @classmethod
    def get_aws_request_id(cls, request):
        """

        :param request:
        :return:
        """
        context = cls.get_lambda_context(request)
        if context:
            return context.aws_request_id
        return uuid.uuid4().__str__()

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
        if halo_context.get(HaloContext.items[HaloContext.DEBUG_LOG]) == 'true' or cls.get_system_debug_enabled() == 'true':
            return True
        return False

    @staticmethod
    def json_error_response(halo_context, clazz, e):  # code, msg, requestId):
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
        if hasattr(e, 'message'):
            e_msg = e.message
        else:
            e_msg = str(e)
        error_detail = ""
        if e_msg is not None and e_msg != 'None' and e_msg != "":
            error_detail = e_msg
        e_payload = {}
        if hasattr(e, 'payload'):
            e_payload = e.payload
        payload = {"error": {"error_code": error_code, "error_message": message, "error_detail": error_detail,
                             "data": e_payload, "trace_id": halo_context.get(HaloContext.items[HaloContext.CORRELATION])}}
        return error_code, json.dumps(payload)