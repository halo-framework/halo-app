from __future__ import print_function

# python
import datetime
import logging
from abc import ABCMeta
import json
import requests
import importlib
# aws
# common
# flask
from flask import Response as HttpResponse

from .utilx import Util, status
from ..const import HTTPChoice
from ..exceptions import *
from ..response import HaloResponse
from ..settingsx import settingsx
from ..logs import log_json
from ..classes import AbsBaseClass
from .servicex import SAGA,SEQ,FoiBusinessEvent,SagaBusinessEvent
from ..apis import AbsBaseApi


settings = settingsx()

# Create your mixin here.

# DRF

# When a service is not responding for a certain amount of time, there should be a fallback path so users are not waiting for the response,
# but are immediately notified about the internal problem with a default response. It is the essence of a responsive design.

logger = logging.getLogger(__name__)

dbaccess = None


class AbsBaseMixinX(AbsBaseClass):
    __metaclass__ = ABCMeta

    name = 'Base'

    def __init__(self):
        self.name = self.get_name()

    # def get_the_template(self, request, name):
    #    return loader.get_template(name)

    def get_root_url(self):
        """

        :return:
        """
        if not settings.STAGE_URL:
            root = '/'
        else:
            root = "/" + settings.ENV_NAME + "/"
        return root

    def get_name(self):
        """

        :return:
        """
        name = self.__class__.__name__
        new_name = name.replace('Link', '')
        return new_name

    def process_get(self, request, vars):
        """

        :param request:
        :param vars:
        :return:
        """
        ret = HaloResponse(HaloRequest(request))
        ret.payload = 'this is process get on '  # + self.get_view_name()
        ret.code = 200
        ret.headers = []
        return ret

    def process_post(self, request, vars):
        """

        :param request:
        :param vars:
        :return:
        """
        ret = HaloResponse(HaloRequest(request))
        ret.payload = 'this is process post on '  # + self.get_view_name()
        ret.code = 201
        ret.headers = []
        return ret

    def process_put(self, request, vars):
        """

        :param request:
        :param vars:
        :return:
        """
        ret = HaloResponse(HaloRequest(request))
        ret.payload = 'this is process put on '  # + self.get_view_name()
        ret.code = 200
        ret.headers = []
        return ret

    def process_patch(self, request, vars):
        """

        :param request:
        :param vars:
        :return:
        """
        ret = HaloResponse(HaloRequest(request))
        ret.payload = 'this is process patch on '  # + self.get_view_name()
        ret.code = 200
        ret.headers = []
        return ret

    def process_delete(self, request, vars):
        """

        :param request:
        :param vars:
        :return:
        """
        ret = HaloResponse(HaloRequest(request))
        ret.payload = 'this is process delete on '  # + self.get_view_name()
        ret.code = 200
        ret.headers = []
        return ret

    def check_author(self, request, vars, json):
        """

        :param request:
        :param vars:
        :param json:
        :return:
        """
        # @TODO check authorization and do masking
        return True, json, None

    def check_authen(self, typer, request, vars):
        """

        :param typer:
        :param request:
        :param vars:
        :return:
        """
        # @TODO check authentication and do masking
        return True, None

class AbsApiMixinX(AbsBaseMixinX):
    __metaclass__ = ABCMeta

    business_event = None


    def create_response(self,halo_request, payload, headers):
        code = status.HTTP_200_OK
        if halo_request.request.method == 'POST' or halo_request.request.method == 'PUT':
            code = status.HTTP_201_CREATED
        return HaloResponse(halo_request, payload, code, headers)

    def validate_req(self, halo_request):
        logger.debug("in validate_req ")
        if halo_request:
            return True
        raise HaloException("Halo Request not valid")

    def validate_pre(self, halo_request):
        if halo_request:
            return True
        raise HaloException("Fail pre validation for Halo Request")

    @staticmethod
    def set_back_api(halo_request, foi=None):
        logger.debug("in set_back_api " + str(foi))
        if foi:
            k = foi.rfind(".")
            module_name = foi[:k]
            class_name = foi[k + 1:]
            module = importlib.import_module(module_name)
            class_ = getattr(module, class_name)
            if not issubclass(class_, AbsBaseApi):
                raise HaloException("class error:" + class_name)
            instance = class_(Util.get_req_context(halo_request.request))
            return instance
        raise HaloException("No api defined")

    @staticmethod
    def set_api_headers(halo_request, seq=None, dict=None):
        logger.debug("in set_api_headers ")
        if halo_request:
            return []
        raise HaloException()

    @staticmethod
    def set_api_vars(halo_request, seq=None, dict=None):
        logger.debug("in set_api_vars " + str(halo_request))
        if True:
            ret = {}
            ret["bq"] = halo_request.behavior_qualifier
            return ret
        raise HaloException()

    @staticmethod
    def set_api_auth(halo_request, seq=None, dict=None):
        return None

    @staticmethod
    def set_api_data(halo_request, seq=None, dict=None):
        return halo_request.request.data

    @staticmethod
    def execute_api(halo_request, back_api, back_vars, back_headers, back_auth, back_data=None, seq=None, dict=None):
        logger.debug("in execute_api "+back_api.name)
        if back_api:
            timeout = Util.get_timeout(halo_request.request)
            try:
                ret = back_api.get(timeout)
                seq_msg = ""
                if seq:
                    seq_msg = "seq = " + seq + "."
                msg = "in execute_api. " + seq_msg + " code= " + str(ret.status_code)
                logger.info(msg)
                return ret
            except ApiError as e:
                raise HaloException(e)
        return None

    @staticmethod
    def extract_json(halo_request, back_response, seq=None):
        logger.debug("in extract_json ")
        if back_response:
            try:
                return json.loads(back_response.content)
            except json.decoder.JSONDecodeError as e:
                pass
        return json.loads("{}")

    def create_resp_payload(self, halo_request, dict_back_json):
        logger.debug("in create_resp_payload " + str(dict_back_json))
        if dict_back_json:
            return dict_back_json
        return {}

    def set_resp_headers(self, halo_request, headers):
        logger.debug("in set_resp_headers " + str(headers))
        if headers:
            return []
        raise HaloException()

    def validate_post(self, halo_request, halo_response):
        return

    def do_operation_bq(self, halo_request):
        if halo_request.behavior_qualifier is None:
            raise IllegalBQException("missing behavior_qualifier value")
        try:
            behavior_qualifier = halo_request.behavior_qualifier.lower()
            # 1. validate input params
            getattr(self, 'validate_req_%s' % behavior_qualifier)(halo_request)
            # 2. Code to access the BANK API  to retrieve data - url + vars dict
            getattr(self, 'validate_pre_%s' % behavior_qualifier)(halo_request)
            # 3. processing engine
            dict = self.processing_engine(halo_request)
            # 4. Build the payload target response structure which is Compliant
            payload = getattr(self, 'create_resp_payload_%s' % behavior_qualifier)(halo_request, dict)
            logger.debug("payload=" + str(payload))
            # 5. setup headers for reply
            headers = getattr(self, 'set_resp_headers_%s' % behavior_qualifier)(halo_request,
                                                                                halo_request.request.headers)
            # 6. build json and add to bian response
            ret = self.create_response(halo_request, payload, headers)
            # 7. post condition
            getattr(self, 'validate_post_%s' % behavior_qualifier)(halo_request, ret)
            # return json response
            return ret
        except AttributeError as ex:
            raise HaloMethodNotImplementedException(ex)

    def do_operation_1_bq(self, halo_request, behavior_qualifier):  # basic maturity - single request
        logger.debug("do_operation_1_bq")
        if behavior_qualifier is None:
            raise IllegalBQException("missing behavior_qualifier value")
        logger.debug("do_operation_1")
        # 1. get api definition to access the BANK API  - url + vars dict
        back_api = getattr(self, 'set_back_api_%s' % behavior_qualifier)(halo_request)
        # 2. array to store the headers required for the API Access
        back_headers = getattr(self, 'set_api_headers_%s' % behavior_qualifier)(halo_request)
        # 3. set request params
        back_vars = getattr(self, 'set_api_vars_%s' % behavior_qualifier)(halo_request)
        # 4. Sset request auth
        back_auth = getattr(self, 'set_api_auth_%s' % behavior_qualifier)(halo_request)
        # 5. Sset request data
        if halo_request.request.method == 'POST' or halo_request.request.method == 'PUT':
            back_data = getattr(self, 'set_api_data_%s' % behavior_qualifier)(halo_request)
        else:
            back_data = None
        # 6. Sending the request to the BANK API with params
        back_response = getattr(self, 'execute_api_%s' % behavior_qualifier)(halo_request, back_api, back_vars,
                                                                             back_headers, back_auth, back_data)
        # 7. extract from Response stored in an object built as per the BANK API Response body JSON Structure
        back_json = getattr(self, 'extract_json_%s' % behavior_qualifier)(halo_request, back_response)
        dict = {1: back_json}
        # 8. return json response
        return dict

    def do_operation_2_bq(self, halo_request, behavior_qualifier):  # medium maturity - foi
        logger.debug("do_operation_2_bq")
        dict = {}
        for seq in self.business_event.keys():
            # 1. get get first order interaction
            foi = self.business_event.get(seq)
            # 2. get api definition to access the BANK API  - url + vars dict
            back_api = getattr(self, 'set_back_api_%s' % behavior_qualifier)(halo_request, foi)
            # 3. array to store the headers required for the API Access
            back_headers = getattr(self, 'set_api_headers_%s' % behavior_qualifier)(halo_request, seq, dict)
            # 4. set vars
            back_vars = getattr(self, 'set_api_vars_%s' % behavior_qualifier)(halo_request, seq, dict)
            # 5. auth
            back_auth = getattr(self, 'set_api_auth_%s' % behavior_qualifier)(halo_request, seq, dict)
            # 6. set request data
            if halo_request.request.method == 'POST' or halo_request.request.method == 'PUT':
                back_data = getattr(self, 'set_api_data_%s' % behavior_qualifier)(halo_request, seq, dict)
            else:
                back_data = None
            # 7. Sending the request to the BANK API with params
            back_response = getattr(self, 'execute_api_%s' % behavior_qualifier)(halo_request, back_api, back_vars,
                                                                                 back_headers, back_auth, back_data,
                                                                                 seq, dict)
            # 8. extract from Response stored in an object built as per the BANK API Response body JSON Structure
            back_json = getattr(self, 'extract_json_%s' % behavior_qualifier)(halo_request, back_response, seq)
            # 9. store in dict
            dict[seq] = back_json
        return dict

    def do_operation(self, halo_request):
        # 1. validate input params
        self.validate_req(halo_request)
        # 2. run pre conditions
        self.validate_pre(halo_request)
        # 3. processing engine
        dict = self.processing_engine(halo_request)
        # 4. Build the payload target response structure which is Compliant
        payload = self.create_resp_payload(halo_request, dict)
        logger.debug("payload=" + str(payload))
        # 5. setup headers for reply
        headers = self.set_resp_headers(halo_request, halo_request.request.headers)
        # 6. build json and add to bian response
        halo_response = self.create_response(halo_request, payload, headers)
        # 7. post condition
        self.validate_post(halo_request, halo_response)
        # 8. return json response
        return halo_response

    def do_operation_1(self, halo_request):  # basic maturity - single request
        logger.debug("do_operation_1")
        # 1. get api definition to access the BANK API  - url + vars dict
        back_api = self.__class__.set_back_api(halo_request)
        # 2. array to store the headers required for the API Access
        back_headers = self.__class__.set_api_headers(halo_request)
        # 3. set request params
        back_vars = self.__class__.set_api_vars(halo_request)
        # 4. Sset request auth
        back_auth = self.__class__.set_api_auth(halo_request)
        # 5. Sset request data
        if halo_request.request.method == 'POST' or halo_request.request.method == 'PUT':
            back_data = self.__class__.set_api_data(halo_request)
        else:
            back_data = None
        # 6. Sending the request to the BANK API with params
        back_response = self.__class__.execute_api(halo_request, back_api, back_vars, back_headers, back_auth,
                                                   back_data)
        # 7. extract from Response stored in an object built as per the BANK API Response body JSON Structure
        back_json = self.__class__.extract_json(halo_request, back_response)
        dict = {1: back_json}
        # 8. return json response
        return dict

    def do_operation_2(self, halo_request):  # medium maturity - foi
        logger.debug("do_operation_2")
        dict = {}
        for seq in self.business_event.keys():
            # 1. get get first order interaction
            foi = self.business_event.get(seq)
            # 2. get api definition to access the BANK API  - url + vars dict
            back_api = __class__.set_back_api(halo_request, foi)
            # 2. do api work
            back_json = self.__class__.do_api_work(halo_request, back_api, seq)
            # 3. store in dict
            dict[seq] = back_json
        return dict

    @staticmethod
    def do_api_work(halo_request, back_api, seq):
        # 3. array to store the headers required for the API Access
        back_headers = __class__.set_api_headers(halo_request, seq, dict)
        # 4. set vars
        back_vars = __class__.set_api_vars(halo_request, seq, dict)
        # 5. auth
        back_auth = __class__.set_api_auth(halo_request, seq, dict)
        # 6. set request data
        if halo_request.request.method == 'POST' or halo_request.request.method == 'PUT':
            back_data = __class__.set_api_data(halo_request, seq, dict)
        else:
            back_data = None
        # 7. Sending the request to the BANK API with params
        back_response = __class__.execute_api(halo_request, back_api, back_vars, back_headers, back_auth,
                                              back_data, seq, dict)
        # 8. extract from Response stored in an object built as per the BANK API Response body JSON Structure
        back_json = __class__.extract_json(halo_request, back_response, seq)
        # return
        return back_json

    def do_saga_work(self, api, results, payload):
        print("do_saga_work=" + str(api) + " result=" + str(results) + "payload=" + str(payload))
        return __class__.do_api_work(payload['request'], api, payload['seq'])

    def do_operation_3(self, halo_request):  # high maturity - saga transactions
        logger.debug("do_operation_3")
        from halo_flask.saga import Saga, SagaRollBack, load_saga
        with open(settings.SAGA_SCHEMA_PATH
                #"C:\\dev\\projects\\halo\\halo_flask\\halo_flask\\tests\\schema.json"
        ) as f1:
            schema = json.load(f1)
        sagax = load_saga("test", self.business_event.saga, schema)
        payloads = {}
        apis = {}
        counter = 1
        for state in self.business_event.saga["States"]:
            if 'Resource' in self.business_event.saga["States"][state]:
                api_name = self.business_event.saga["States"][state]['Resource']
                print(api_name)
                payloads[state] = {"request": halo_request, 'seq': str(counter)}
                apis[state] = self.do_saga_work
                counter = counter + 1

        # payloads = {"BookHotel": {"abc": "def"}, "BookFlight": {"abc": "def"}, "BookRental": {"abc": "def"},
        #            "CancelHotel": {"abc": "def"}, "CancelFlight": {"abc": "def"}, "CancelRental": {"abc": "def"}}
        # apis = {"BookHotel": self.create_api1, "BookFlight": self.create_api2, "BookRental": self.create_api3,
        #        "CancelHotel": self.create_api4, "CancelFlight": self.create_api5, "CancelRental": self.create_api6}
        try:
            ret = sagax.execute(Util.get_req_context(halo_request.request), payloads, apis)
            return ret
        except SagaRollBack as e:
            ret = HaloResponse(halo_request)
            ret.payload = {"test": "bad"}
            ret.code = 500
            ret.headers = []
            return ret

    def processing_engine(self, halo_request):
        if self.business_event:
            if self.business_event.get_business_event_type() == SAGA:
                if halo_request.behavior_qualifier:
                    return self.do_operation_3_bq(halo_request, halo_request.behavior_qualifier.lower())
                return self.do_operation_3(halo_request)
            if self.business_event.get_business_event_type() == SEQ:
                if self.business_event.keys():
                    if halo_request.behavior_qualifier:
                        return self.do_operation_2_bq(halo_request, halo_request.behavior_qualifier.lower())
                    return self.do_operation_2(halo_request)
                else:
                    raise BusinessEventMissingSeqException(self.service_operation)
        else:
            if halo_request.behavior_qualifier:
                return self.do_operation_1_bq(halo_request, halo_request.behavior_qualifier.lower())
            return self.do_operation_1(halo_request)

    def set_businss_event(self, request, event_category):
       self.service_operation = request.path
       if not self.business_event:
            if settings.BUSINESS_EVENT_MAP:
                if self.service_operation in settings.BUSINESS_EVENT_MAP:
                    service_list = settings.BUSINESS_EVENT_MAP[self.service_operation]
                    #@todo add schema to all event config files
                    if request.method in service_list:
                        service_map = service_list[request.method]
                        if SEQ in service_map:
                            dict = service_map[SEQ]
                            self.business_event = FoiBusinessEvent(self.service_operation,event_category, dict)
                        if SAGA in service_map:
                            saga = service_map[SAGA]
                            self.business_event = SagaBusinessEvent(self.service_operation, event_category, saga)
                    else:
                        raise BusinessEventMissingSeqException(request.method)
       return self.business_event

class PerfMixinX(AbsBaseMixinX):
    now = None

    def process_get(self, request, vars):
        self.now = datetime.datetime.now()
        db = request.args.get('db', None)
        urls = {}
        if settings.SSM_APP_CONFIG:
            if settings.SSM_APP_CONFIG.cache:
                logger.debug('perf: ' + str(settings.SSM_APP_CONFIG.cache.items))
                for item in settings.SSM_APP_CONFIG.cache.items:
                    logger.debug("item=" + str(item))
                    if item not in [settings.FUNC_NAME, 'DEFAULT']:
                        rec = settings.SSM_APP_CONFIG.get_param(item)
                        if "url" in rec:
                            url = rec["url"]
                        else:
                            logger.error("service " + item + " in API_CONFIG is set to None in cache/store")
                            continue
                        logger.debug("got url for " + item + ":" + url)
                        if settings.FRONT_WEB is True:
                            if db is not None:
                                s = '?db=' + db
                            else:
                                s = ''
                            ret = requests.get(url + "/perf" + s)
                            urls[item] = {"url": url, "ret": str(ret.content)}
                        else:
                            urls[item] = {"url": url, "ret": ''}
                        for key in settings.API_CONFIG:
                            current = settings.API_CONFIG[key]
                            new_url = current["url"]
                            if "service://" + item in new_url:
                                settings.API_CONFIG[key]["url"] = new_url.replace("service://" + item, url)
        logger.debug(str(settings.API_CONFIG))
        ret = ''
        if db is not None:
            ret = self.process_db(request, vars)
        total = datetime.datetime.now() - self.now
        # return HttpResponse('performance page: timing for process: ' + str(total) + " " + str(urls) + " " + ret + " " + settings.VERSION)
        return HaloResponse(request,{"msg": 'performance page: timing for process: ' + str(total) + " " + str(
            urls) + " " + ret + " " + settings.VERSION}, 200, [])


    def process_db(self, request, vars):
        logger.debug('db perf: ')
        total = datetime.datetime.now() - self.now
        return 'db access: ' + str(total)


class AbsAuthMixinX(AbsBaseMixinX):
    __metaclass__ = ABCMeta

    name = 'Api'
    class_name = None
    correlate_id = None
    #req_context = None

    def __init__(self):
        AbsBaseMixinX.__init__(self)
        self.class_name = self.__class__.__name__

    def process_in_auth(self, typer, request, vars):
        # who can use this resource with this method - api product,app,user,role,scope
        ret, cause = self.check_authen(typer, request, vars)
        if ret:
            ctx = Util.get_auth_context(request)
            req_context = Util.get_req_context(request)
            logger.debug("ctx:" + str(ctx), extra=log_json(req_context))
            return ctx
        raise AuthException(request, cause)

    def process_out_auth(self, request, vars, json):
        ret, jsonx, cause = self.check_author(request, vars, json)
        # who can use this model with this method - object,field
        if ret:
            req_context = Util.get_req_context(request)
            logger.debug("jsonx:" + str(jsonx), extra=log_json(req_context))
            return jsonx
        raise AuthException(request, cause)

    # raise AuthException(typer,resource,cause)

    def process_get(self, request, vars):
        try:
            ctx = self.process_in_auth(HTTPChoice.get, request, vars)
        except AuthException as e:
            return HttpResponse(e.cause, status=status.HTTP_400_BAD_REQUEST)
        ret = self.process_api(ctx, HTTPChoice.get, request, vars)
        if ret.code == status.HTTP_200_OK:
            jsonx = self.process_out_auth(request, vars, ret.payload)
            ret.payload = jsonx
        return ret  #Util.json_data_response(jsonx, ret.status_code)  # HttpResponse(jsonx, status=ret_status)

    def process_post(self, request, vars):
        try:
            ctx = self.process_in_auth(HTTPChoice.post, request, vars)
        except AuthException as e:
            return HttpResponse(e.cause, status=status.HTTP_400_BAD_REQUEST)
        ret = self.process_api(ctx, HTTPChoice.post, request, vars)
        if ret.code == status.HTTP_201_CREATED:
            jsonx = self.process_out_auth(request, vars, json)
            ret.payload = jsonx
        return ret

    def process_put(self, request, vars):
        try:
            ctx = self.process_in_auth(HTTPChoice.put, request, vars)
        except AuthException as e:
            return HttpResponse(e.cause, status=status.HTTP_400_BAD_REQUEST)
        ret = self.process_api(ctx, HTTPChoice.put, request, vars)
        if ret.code == status.HTTP_202_ACCEPTED:
            jsonx = self.process_out_auth(request, vars, json)
            ret.payload = jsonx
        return ret

    def process_patch(self, request, vars):
        try:
            ctx = self.process_in_auth(HTTPChoice.patch, request, vars)
        except AuthException as e:
            return HttpResponse(e.cause, status=status.HTTP_400_BAD_REQUEST)
        ret = self.process_api(ctx, HTTPChoice.patch, request, vars)
        if ret.code == status.HTTP_202_ACCEPTED:
            jsonx = self.process_out_auth(request, vars, json)
            ret.payload = jsonx
        return ret

    def process_delete(self, request, vars):
        try:
            ctx = self.process_in_auth(HTTPChoice.delete, request, vars)
        except AuthException as e:
            return HttpResponse(e.cause, status=status.HTTP_400_BAD_REQUEST)
        ret = self.process_api(ctx, HTTPChoice.delete, request, vars)
        if ret.code == status.HTTP_200_OK:
            jsonx = self.process_out_auth(request, vars, json)
            ret.payload = jsonx
        return ret

    def process_api(self, ctx, typer, request, vars):
        return {}, 200

##############################################################################3

from halo_flask.logs import log_json
from halo_flask.exceptions import ApiError, ApiException
from halo_flask.saga import load_saga, SagaRollBack
from halo_flask.flask.mixinx import AbsApiMixinX
from halo_flask.response import HaloResponse
from halo_flask.request import HaloRequest
from halo_flask.apis import CnnApi


class TestMixinX(AbsApiMixinX):

    def set_back_api(halo_request):
        req_context = Util.get_req_context(halo_request.request)
        api = CnnApi(req_context)
        return api

    def process_get(self, request, vars):
        halo_request = HaloRequest(request)
        self.set_businss_event(request, "x")
        ret = self.do_operation(halo_request)
        if ret.code == status.HTTP_200_OK:
            print(str(ret.payload))
        return ret

    def process_put(self, request, vars):
        halo_request = HaloRequest(request)
        self.set_businss_event(request, "x")
        ret = self.do_operation(halo_request)
        if ret.code == status.HTTP_200_OK:
            print(str(ret.payload))
        return ret

class TestMixinX1(AbsAuthMixinX):

    def process_api(self, ctx, typer, request, vars):
        self.upc = "123"
        self.typer = typer
        if typer == typer.get:
            logger.debug("start get")
            req_context = Util.get_req_context(request)
            api = CnnApi(req_context)
            # api.set_api_url("upcid", upc)
            # api.set_api_query(request)
            timeout = Util.get_timeout(request)
            try:
                ret = api.get(timeout)
            except ApiError as e:
                logger.debug("we did it", extra=log_json(req_context, Util.get_req_params(request), e))
                ret = HaloResponse()
                ret.payload = {"test1": "bad"}
                ret.code = 400
                ret.headers = []
                return ret
            # except NoReturnApiException as e:
            #    print("NoReturnApiException="+e.message)
            # log_json(self.req_context, LogLevels.DEBUG._name_, "we did it", Util.get_req_params(request))
            ret = HaloResponse()
            ret.payload = {"test2": "good"}
            ret.code = 200
            ret.headers = []
            return ret

        if typer == typer.post or typer == typer.put:
            logger.debug("start " + str(typer))
            with open("C:\\dev\\projects\\halo\\halo_flask\\halo_flask\\tests\\saga.json") as f:
                jsonx = json.load(f)
            with open("C:\\dev\\projects\\halo\\halo_flask\\halo_flask\\tests\\schema.json") as f1:
                schema = json.load(f1)
            sagax = load_saga("test", jsonx, schema)
            payloads = {"BookHotel": {"abc": "def"}, "BookFlight": {"abc": "def"}, "BookRental": {"abc": "def"},
                        "CancelHotel": {"abc": "def"}, "CancelFlight": {"abc": "def"}, "CancelRental": {"abc": "def"}}
            apis = {"BookHotel": self.create_api1, "BookFlight": self.create_api2, "BookRental": self.create_api3,
                    "CancelHotel": self.create_api4, "CancelFlight": self.create_api5, "CancelRental": self.create_api6}
            try:
                self.context = Util.get_lambda_context(request)
                req_context = Util.get_req_context(request)
                ret = sagax.execute(req_context, payloads, apis)
                ret = HaloResponse()
                ret.payload = {"test": "good"}
                ret.code = 200
                ret.headers = []
                return ret
            except SagaRollBack as e:
                ret = HaloResponse()
                ret.payload = {"test": "bad"}
                ret.code = 500
                ret.headers = []
                return ret
        if typer == typer.delete:
            raise ApiException("test error msg")

    def create_api1(self, api, results, payload):
        print("create_api1=" + str(api) + " result=" + str(results))
        api.set_api_url("upcid", self.upc)
        if self.context:
            timeout = Util.get_timeout_milli(self.context)
        else:
            timeout = 100
        return api.get(timeout)

    def create_api2(self, api, results, payload):
        print("create_api2=" + str(api) + " result=" + str(results))
        api.set_api_url("upcid", self.upc)
        if self.context:
            timeout = Util.get_timeout_milli(self.context)
        else:
            timeout = 100
        return api.get(timeout)

    def create_api3(self, api, results, payload):
        print("create_api3=" + str(api) + " result=" + str(results))
        api.set_api_url("upcid", self.upc)
        if self.context:
            timeout = Util.get_timeout_milli(self.context)
        else:
            timeout = 100
        if self.typer == self.typer.post:
            return api.post(payload, timeout)
        return api.get(timeout)

    def create_api4(self, api, results, payload):
        print("create_api4=" + str(api) + " result=" + str(results))
        api.set_api_url("upcid", self.upc)
        if self.context:
            timeout = Util.get_timeout_milli(self.context)
        else:
            timeout = 100
        return api.get(timeout)

    def create_api5(self, api, results, payload):
        print("create_api5=" + str(api) + " result=" + str(results))
        api.set_api_url("upcid", self.upc)
        if self.context:
            timeout = Util.get_timeout_milli(self.context)
        else:
            timeout = 100
        return api.get(timeout)

    def create_api6(self, api, results, payload):
        print("create_api6=" + str(api) + " result=" + str(results))
        api.set_api_url("upcid", self.upc)
        if self.context:
            timeout = Util.get_timeout_milli(self.context)
        else:
            timeout = 100
        return api.get(timeout)


