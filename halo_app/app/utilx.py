from __future__ import print_function

import json
# python
import logging
import os
import random
import importlib

from halo_app.classes import AbsBaseClass
from halo_app.app.context import HaloContext, InitCtxFactory
from halo_app.exceptions import CacheError, ProviderError
from halo_app.providers.providers import get_provider,ONPREM
from ..reflect import Reflect
from ..settingsx import settingsx

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

    def init_halo_context(self):
        context = Util.get_halo_context()
        if settings.HALO_CONTEXT_CLASS:
            context = Reflect.instantiate(settings.HALO_CONTEXT_CLASS,HaloContext)
        return context

    @classmethod
    def get_timeout(cls, halo_context:HaloContext):
        """

        :param request:
        :return:
        """
        if "timeout" in halo_context.keys():
            timeout = halo_context.get("timeout")
            if timeout:
                return timeout
        return settings.SERVICE_CONNECT_TIMEOUT_IN_SC

    @classmethod
    def get_halo_timeout1(cls, halo_request):
        """

        :param request:
        :return:
        """
        if "timeout" in halo_request.context.keys():
            timeout = halo_request.context.get("timeout")
            if timeout:
                return timeout
        return settings.SERVICE_CONNECT_TIMEOUT_IN_SC


    @classmethod
    def get_halo_context(cls, api_key=None,x_correlation_id=None,x_user_agent=None,dlog=None,request_id=None):
        """
        :param request:
        :param api_key:
        :return:
        """

        env = {HaloContext.items[HaloContext.USER_AGENT]: x_user_agent,
               HaloContext.items[HaloContext.REQUEST]: request_id,
               HaloContext.items[HaloContext.CORRELATION]: x_correlation_id,
               HaloContext.items[HaloContext.DEBUG_LOG]: dlog}
        if api_key:
            env[HaloContext.items[HaloContext.API_KEY]] = api_key
        ctx = InitCtxFactory.get_initial_context(env)
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
    def isDebugEnabled(cls, halo_context):
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
    def json_error_response(halo_context,args, clazz, e):  # code, msg, requestId):
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
            error_detail = Util.get_detail(e.original_exception)
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
            payload["request"] = json.dumps(args)
        return payload

    @staticmethod
    def get_detail(e):
        detail = None
        if e.original_exception:
            detail = Util.get_detail(e.original_exception)
        if detail:
            return str(e)+':'+detail
        return str(e)


