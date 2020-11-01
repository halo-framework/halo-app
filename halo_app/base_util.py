from __future__ import print_function

import importlib
import json
# python
import logging
import os
import random
import uuid
import datetime
import jwt
from jsonschema import validate
from .exceptions import CacheError, ApiTimeOutExpired
from halo_app.const import LOC,DEV,TST,PRD
from halo_app.context import HaloContext
from halo_app.response import HaloResponse
from halo_app.classes import AbsBaseClass
from .settingsx import settingsx
settings = settingsx()

logger = logging.getLogger(__name__)

class BaseUtil(AbsBaseClass):

    def __init__(self):
        pass

    event_req_context = None

    @staticmethod
    def assert_valid_schema(data, schema):
        """ Checks whether the given saga json matches the schema """

        return validate(data, schema)


    @staticmethod
    def get_stage():
        """

        :return:
        """
        if 'HALO_STAGE' in os.environ:
            return os.environ['HALO_STAGE']
        return LOC

    @staticmethod
    def get_type():
        """

        :return:
        """
        if 'HALO_TYPE' in os.environ:
            return os.environ['HALO_TYPE']
        return LOC

    @staticmethod
    def get_func():
        """

        :return:
        """
        if 'HALO_FUNC_NAME' in os.environ:
            return os.environ['HALO_FUNC_NAME']
        return settings.FUNC_NAME

    @staticmethod
    def get_app():
        """

        :return:
        """
        if 'HALO_APP_NAME' in os.environ:
            return os.environ['HALO_APP_NAME']
        return settings.APP_NAME

    @staticmethod
    def get_host_name():
        if 'HALO_HOST' in os.environ:
            return os.environ['HALO_HOST']
        return settings.HALO_HOST

    @classmethod
    def get_context(cls):
        """

        :return:
        """
        ret = {"awsRegion": cls.get_func_region(), "functionName": cls.get_func_name(),
               "functionVersion": cls.get_func_ver(), "functionMemorySize": cls.get_func_mem(),
               "stage": cls.get_stage()}
        return ret


    @staticmethod
    def get_env():
        env = BaseUtil.get_stage()
        print("stage:" + str(env))
        type = BaseUtil.get_type()
        print("type:" + str(type))
        app_config_path = BaseUtil.get_func()
        print("func_name:" + str(app_config_path))
        app_name = BaseUtil.get_app()
        print("app_name:" + str(app_name))
        full_config_path = '/' + app_name + '/' + env + '/' + app_config_path
        short_config_path = '/' + app_name + '/' + type + '/service'
        return full_config_path, short_config_path

    @classmethod
    def get_correlation_from_event(cls, event):
        """

        :param event:
        :return:
        """
        #@todo refactor provider data into the method
        if cls.event_req_context:
            logger.debug("cached event req_context", extra=cls.event_req_context)
            return cls.event_req_context
        correlate_id = ''
        user_agent = ''
        debug_flag = ''
        # from api gateway
        if "httpMethod" in event and "requestContext" in event:
            if "headers" in event:
                headers = event["headers"]
                # get correlation-id
                if HaloContext.items[HaloContext.CORRELATION] in headers:
                    correlate_id = headers[HaloContext.items[HaloContext.CORRELATION]]
                else:
                    if "aws_request_id" in headers:
                        correlate_id = headers["aws_request_id"]
                    else:
                        correlate_id = uuid.uuid4().__str__()
                # get user-agent = get_func_name + ':' + path + ':' + request.method + ':' + host_ip
                if "x-user-agent" in headers:
                    user_agent = headers["x-user-agent"]
                else:
                    if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
                        func_name = os.environ['AWS_LAMBDA_FUNCTION_NAME']
                    else:
                        if "apiId" in event["requestContext"]:
                            func_name = event["requestContext"]["apiId"]
                        else:
                            func_name = headers["Host"]
                    if "path" in event["requestContext"]:
                        path = event["requestContext"]["path"]
                    else:
                        path = "path"
                    if "httpMethod" in event:
                        method = event["httpMethod"]
                    else:
                        if "httpMethod" in event["requestContext"]:
                            method = event["requestContext"]["httpMethod"]
                        else:
                            method = "method"
                    host_ip = "12.34.56.78"
                    user_agent = str(func_name) + ':' + str(path) + ':' + str(method) + ':' + str(host_ip)
                    logger.debug("user_agent:" + user_agent, extra=cls.event_req_context)
        # from other source
        else:
            if HaloContext.items[HaloContext.CORRELATION] in event:
                correlate_id = event[HaloContext.items[HaloContext.CORRELATION]]
            if HaloContext.items[HaloContext.USER_AGENT] in event:
                user_agent = event[HaloContext.items[HaloContext.USER_AGENT]]
            if HaloContext.items[HaloContext.DEBUG_LOG] in event:
                debug_flag = event[HaloContext.items[HaloContext.DEBUG_LOG]]
        ret = {HaloContext.items[HaloContext.USER_AGENT]: user_agent, HaloContext.items[HaloContext.REQUEST]: '',
               HaloContext.items[HaloContext.CORRELATION]: correlate_id, HaloContext.items[HaloContext.DEBUG_LOG]: debug_flag}
        if HaloContext.items[HaloContext.API_KEY] in event:
            ret[HaloContext.items[HaloContext.API_KEY]] = event[HaloContext.items[HaloContext.API_KEY]]
        # @TODO get all data for request context
        cls.event_req_context = ret
        return cls.event_req_context


