from __future__ import print_function

# python
import logging
import json
import re
from jsonpath_ng import parse
# aws
# common
# app
from .exceptions import BadRequestError, HaloMethodNotImplementedException, BusinessEventMissingSeqException, \
    BusinessEventNotImplementedException, ServerError, ConvertDomainExceptionHandler
from .uow import AbsUnitOfWork
from halo_app.app.context import HaloContext
from ..domain.exceptions import DomainException
from ..errors import status
from ..const import HTTPChoice, ASYNC, BusinessEventCategory
from ..entrypoints.client_type import ClientType
from ..exceptions import *
from ..infra.engine import ProcessingEngine
from ..reflect import Reflect
from halo_app.app.request import AbsHaloRequest, HaloEventRequest, HaloCommandRequest, HaloQueryRequest
from halo_app.app.response import AbsHaloResponse
from ..settingsx import settingsx
from ..classes import AbsBaseClass
from .business_event import BusinessEventCategory, FoiBusinessEvent, SagaBusinessEvent, ApiBusinessEvent, BusinessEvent
from halo_app.infra.apis import ApiMngr
from .anlytx_filter import RequestFilter
from halo_app.infra.providers.providers import get_provider
from halo_app.saga import SagaRollBack, load_saga
from halo_app.app.utilx import Util
from ..sys_util import SysUtil

settings = settingsx()

# Create your mixin here.

# DRF

# When a service is not responding for a certain amount of time, there should be a fallback path so users are not waiting for the response,
# but are immediately notified about the internal problem with a default response. It is the essence of a responsive design.

logger = logging.getLogger(__name__)


class AbsBaseHandler(AbsBaseClass):
    __metaclass__ = ABCMeta

    business_event = None
    secure = False
    method_roles = None

    @abstractmethod
    def __init__(self,method_id=None):
        pass

    def validate_req(self, halo_request):
        logger.debug("in validate_req ")
        if halo_request:
            return True
        raise BadRequestError("Halo Request not valid")

    def validate_pre(self, halo_request):
        if halo_request:
            return True
        raise BadRequestError("Fail pre validation for Halo Request")

    def create_resp_payload(self, halo_request, dict_back_json):
        logger.debug("in create_resp_payload " + str(dict_back_json))
        if dict_back_json:
            mapping = self.load_resp_mapping(halo_request)
            if mapping:
                try:
                    jsonpath_expression = parse(str(mapping))
                    matchs = jsonpath_expression.find(dict_back_json)
                    for match in matchs:
                        logger.debug( match.value)
                    ret = self.create_resp_json(halo_request, dict_back_json,matchs)
                    return ret
                except Exception as e:
                    logger.debug(str(e))
                    raise HaloException("mapping error for " + halo_request.method_id,e)
            ret = self.create_resp_json(halo_request, dict_back_json)
            return ret
        return {}

    def create_resp_json(self, halo_request, dict_back_json, matchs=None):
        logger.debug("in create_resp_json ")
        if matchs:
            js = {}
            try:
                for match in matchs:
                    logger.debug(match.value)
                    js[match.path] = match.value
                    return js
            except Exception as e:
                pass
        else:
            if type(dict_back_json) is dict:
                if len(dict_back_json) == 1:
                    if 1 in dict_back_json:
                        return dict_back_json[1]
                    return list(dict_back_json.values())[0]
                else:
                    return self.dict_to_json(dict_back_json)
        return dict_back_json

    def dict_to_json(self, dict_back_json):
        return dict_back_json

    def load_resp_mapping1(self, halo_request):
        logger.debug("in load_resp_mapping " + str(halo_request))
        if settings.MAPPING and halo_request.method_id in settings.MAPPING:
            mapping = settings.MAPPING[halo_request.method_id]
            logger.debug("in load_resp_mapping " + str(mapping))
            return mapping
        raise HaloException("no mapping for "+halo_request.method_id)

    def load_resp_mapping(self, halo_request):
        logger.debug("in load_resp_mapping " + str(halo_request))
        if settings.MAPPING:
            for path in settings.MAPPING:
                try:
                    if re.match(path,halo_request.method_id):
                        mapping = settings.MAPPING[path]
                        logger.debug("in load_resp_mapping " + str(mapping))
                        return mapping
                except Exception as e:
                    logger.debug("error in load_resp_mapping " + str(path))
        return None

    def set_resp_headers1(self, halo_request, headers=None):
        logger.debug("in set_resp_headers " + str(headers))
        if headers:
            headersx = {}
            for h in headers:
                if h in headers:
                    headersx[h] = headers[h]
            headersx['mimetype'] = 'application/json'
            return headersx
        #raise HaloException("no headers")
        return []

    def validate_post(self, halo_request, halo_response):
        if True:
            return halo_response
        raise ServerError(halo_response)


    def do_filter(self, halo_request, halo_response):  #
        logger.debug("do_filter")
        request_filter = self.get_request_filter(halo_request)
        request_filter.do_filter(halo_request, halo_response)

    def get_request_filter(self, halo_request):
        if settings.REQUEST_FILTER_CLASS:
            return Reflect.instantiate(settings.REQUEST_FILTER_CLASS, RequestFilter)
        return RequestFilter()

class AbsQueryHandler(AbsBaseHandler):
    __metaclass__ = ABCMeta

    @abstractmethod
    def do_operation(self, halo_request:AbsHaloRequest)->AbsHaloResponse:
        # 1. validate input params
        self.validate_req(halo_request)
        # 2. run pre conditions
        self.validate_pre(halo_request)
        # 3. processing engine
        dict_dto = self.data_engine(halo_request)
        # 4. Build the payload target response structure which is Compliant
        payload = self.create_resp_payload(halo_request, dict_dto)
        logger.debug("payload=" + str(payload))
        # 5. setup headers for reply
        #headers = self.set_resp_headers(halo_request)
        # 6. build json and add to halo response
        halo_response = Util.create_response(halo_request,True, payload)
        # 7. post condition
        self.validate_post(halo_request, halo_response)
        # 8. do filter
        #self.do_filter(halo_request,halo_response)
        # 9. return json response
        return halo_response

    def data_engine(self,halo_request:HaloQueryRequest)->dict:
        return self.run(halo_request,self.uow)

    def set_query_data(self,halo_query_request: HaloQueryRequest):
        raise HaloMethodNotImplementedException("method set_query_data in Query")

    def run(self, halo_query_request: HaloQueryRequest,uow:AbsUnitOfWork) -> dict:
        query_str, dict_params = self.set_query_data(halo_query_request)
        with uow:
            results = list(uow.session.execute(query_str, dict_params))
        return results

    def __run_query(self,halo_request:HaloQueryRequest,uow:AbsUnitOfWork)->AbsHaloResponse:
        self.uow = uow
        ret:AbsHaloResponse = self.do_operation(halo_request)
        return ret

    @classmethod
    def run_query_class(cls,halo_request:HaloQueryRequest,uow:AbsUnitOfWork)->AbsHaloResponse:
        handler = cls()
        return handler.__run_query(halo_request,uow)

class AbsEventHandler(AbsBaseHandler):
    __metaclass__ = ABCMeta

    @abstractmethod
    def do_operation(self, halo_request:AbsHaloRequest):
        # 1. validate input params
        self.validate_req(halo_request)
        # 2. run pre conditions
        self.validate_pre(halo_request)
        # 3. processing engine
        self.event_engine(halo_request)


    def event_engine(self, halo_request:HaloEventRequest):
        self.handle(halo_request,self.uow)

    def handle(self,halo_event_request:HaloEventRequest,uow:AbsUnitOfWork):
        raise HaloMethodNotImplementedException("method handle in command")

    def _run_event(self, halo_request:HaloEventRequest,uow:AbsUnitOfWork):
        self.uow = uow
        ret:AbsHaloResponse = self.do_operation(halo_request)

    @classmethod
    def run_event_class(cls,halo_request:HaloEventRequest,uow:AbsUnitOfWork)->AbsHaloResponse:
        handler = cls()
        return handler._run_event(halo_request,uow)

class AbsCommandHandler(AbsBaseHandler):
    __metaclass__ = ABCMeta

    # each handler injects the following:
    # DomainService
    # InfrastructureService
    # Repository

    def set_back_api(self, halo_request):
        return None

    @abstractmethod
    def do_operation(self, halo_request:AbsHaloRequest)->AbsHaloResponse:
        # 1. validate input params
        self.validate_req(halo_request)
        # 2. run pre conditions
        self.validate_pre(halo_request)
        # 3. processing engine
        table = self.processing_engine(halo_request)
        # 4. Build the payload target response structure which is Compliant
        payload = self.create_resp_payload(halo_request, table)
        #logger.debug("payload=" + str(payload))
        # 5. setup headers for reply
        #headers = self.set_resp_headers(halo_request)
        # 6. build json and add to halo response
        halo_response = Util.create_response(halo_request,True,payload)
        # 7. post condition
        self.validate_post(halo_request, halo_response)
        # 8. do filter
        self.do_filter(halo_request,halo_response)
        # 9. return json response
        return halo_response

    def processing_engine(self, halo_request:HaloCommandRequest)->dict:
        domain_exception_handler = ConvertDomainExceptionHandler()
        try:
            if self.business_event:
                return self.processing_engine_dtl(halo_request)
            else:
                return self.handle(halo_request,self.uow)
        except DomainException as e:
            raise domain_exception_handler.handle(e)

    def processing_engine_dtl(self, halo_request:HaloCommandRequest)->dict:
        if self.business_event:
            processing_engine = ProcessingEngine(self.business_event,self.set_back_api(halo_request))
            if self.business_event.get_business_category() == BusinessEventCategory.SAGA:
                return processing_engine.do_operation_3(halo_request)
            if self.business_event.get_business_category() == BusinessEventCategory.SEQ:
                if self.business_event.keys():
                    return processing_engine.do_operation_2(halo_request)
                else:
                    raise BusinessEventMissingSeqException(self.service_operation)
            else:
                return processing_engine.do_operation_1(halo_request)
        raise BusinessEventNotImplementedException("business_event for command method id:"+halo_request.method_id)

    def handle(self,halo_command_request:HaloCommandRequest,uow:AbsUnitOfWork)->dict:
        raise HaloMethodNotImplementedException("method handle in command")


    def set_businss_event(self, halo_request:HaloCommandRequest, event_category:BusinessEventCategory=None):
       self.service_operation = SysUtil.instance_full_name(self)#self.__class__.__name__
       if not self.business_event:
            if settings.BUSINESS_EVENT_MAP:
                if self.service_operation in settings.BUSINESS_EVENT_MAP:
                    #bq = "base"
                    bqs = settings.BUSINESS_EVENT_MAP[self.service_operation]
                    for bq in bqs:
                        service_list = bqs[bq]
                        #@todo add schema to all event config files
                        if service_list and halo_request.method_id in service_list.keys():
                            service_map = service_list[halo_request.method_id]
                            if BusinessEventCategory.EMPTY.value in service_map:
                                dict = service_map[BusinessEventCategory.EMPTY.value]
                                self.business_event = BusinessEvent(self.service_operation,BusinessEventCategory.EMPTY)
                            if BusinessEventCategory.API.value in service_map:
                                dict = service_map[BusinessEventCategory.API.value]
                                self.business_event = ApiBusinessEvent(self.service_operation,BusinessEventCategory.API, dict)
                            if BusinessEventCategory.SEQ.value in service_map:
                                dict = service_map[BusinessEventCategory.SEQ.value]
                                self.business_event = FoiBusinessEvent(self.service_operation,BusinessEventCategory.SEQ, dict)
                            if BusinessEventCategory.SAGA.value in service_map:
                                saga = service_map[BusinessEventCategory.SAGA.value]
                                self.business_event = SagaBusinessEvent(self.service_operation, BusinessEventCategory.SAGA, saga)
                    #   if no entry use simple operation

    ######################################################################

    def __run_command(self,halo_request:HaloCommandRequest,uow:AbsUnitOfWork)->AbsHaloResponse:
        self.uow = uow
        self.set_businss_event(halo_request, BusinessEventCategory.EMPTY)
        ret:AbsHaloResponse = self.do_operation(halo_request)
        return ret

    @classmethod
    def run_command_class(cls,halo_request:HaloCommandRequest,uow:AbsUnitOfWork)->AbsHaloResponse:
        handler = cls()
        return handler.__run_command(halo_request,uow)





