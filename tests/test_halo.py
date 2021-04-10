from __future__ import print_function

import json
import os
from dataclasses import dataclass
from http import HTTPStatus
from faker import Faker
from flask import Flask, request
from nose.tools import eq_

from halo_app.app.dto_assembler import DtoAssemblerFactory, AbsDtoAssembler
from halo_app.app.dto_mapper import AbsHaloDtoMapper
from halo_app.app.handler import AbsCommandHandler, AbsEventHandler, AbsQueryHandler
from halo_app.app.notification import Notification
from halo_app.app.response import AbsHaloResponse, HaloResponseFactory, HaloCommandResponse
from halo_app.app.result import Result
from halo_app.app.uow import AbsUnitOfWork
from halo_app.base_util import BaseUtil
from halo_app.app.event import AbsHaloEvent
from halo_app.domain.entity import AbsHaloEntity
from halo_app.domain.exceptions import AbsDomainException
from halo_app.domain.model import Item
from halo_app.app.dto import AbsHaloDto
from halo_app.entrypoints import client_util
from halo_app.infra.impl.redis_event_publisher import Publisher
from halo_app.infra.sql_uow import SqlAlchemyUnitOfWork
from halo_app.app.query import HaloQuery
from halo_app.domain.service import AbsDomainService
from halo_app.infra.exceptions import ApiException, AbsInfraException
from halo_app.app.exceptions import HaloMethodNotImplementedException
from halo_app.domain.repository import AbsRepository
from halo_app.infra.mail import AbsMailService
from halo_app.logs import log_json
from halo_app import saga
from halo_app.const import HTTPChoice, OPType
from halo_app.entrypoints.client_type import ClientType
from tests.fake import FakeBoundary, FakePublisher
from halo_app.infra.apis import AbsRestApi, AbsSoapApi, SoapResponse, ApiMngr  # CnnApi,GoogleApi,TstApi
from halo_app.app.boundary import BoundaryService
from halo_app.app.request import HaloContext, HaloCommandRequest, HaloEventRequest, HaloQueryRequest
from halo_app.infra.apis import load_api_config
from halo_app.models import AbsDbMixin
from halo_app.ssm import set_app_param_config,get_app_param_config,set_host_param_config
from halo_app.app.globals import load_global_data
from halo_app.security import HaloSecurity
from halo_app.app.utilx import Util
from halo_app.sys_util import SysUtil
from halo_app.app.request import AbsHaloRequest

import unittest
import pytest

from tests.fake import FakeConsumer

faker = Faker()
app = Flask(__name__)


##################################### test #########################
"""
###performance testing###
npm install -g artillery
artillery -V
artillery quick --count 10 -n 20 http://127.0.0.1:5000/loc/info
artillery run artilery.yml
config:
  target: 'http://127.0.0.1:5000'
  phases:
    - duration: 60
      arrivalRate: 20
  defaults:
    headers:
      x-my-service-auth: '987401838271002188298567'
scenarios:
  - flow:
    - get:
        url: "/loc/info"

"""


class CnnApi(AbsRestApi):
    name = 'Cnn'


class GoogleApi(AbsRestApi):
    name = 'Google'

class TstApi(AbsRestApi):
    name = 'Tst'

class Tst2Api(AbsSoapApi):
    name = 'Tst2'

    def do_method1(self,timeout, data=None, headers=None, auth=None):
        if not data:
            data = {"first":"one",'second':"two"}
        soap_ret = self.client.service.Method1(data["first"], data['second'])
        print(str(soap_ret))
        content = json.dumps({"msg":soap_ret})
        response = SoapResponse(content,{},200)
        return response

class Tst3Api(AbsRestApi):
    name = 'Tst3'

class Tst4Api(AbsRestApi):
    name = 'Tst4'

class AwsApi(AbsRestApi):
    name = 'halo-webapp-service-dev-halo_webapp'

class PrimoServiceApi(AbsRestApi):
    name='PrimoService-dev-hello'

class DbTest(AbsDbMixin):
    pass
class DbMixin(AbsDbMixin):
    pass


class Sec(HaloSecurity):
    def get_secret(self):
        return '12345'
    def get_user_roles(self,user):
        return ['tst']

#API_LIST = {"Google": 'tests.test_halo.GoogleApi', "Cnn": "tests.test_halo.CnnApi","Tst":"tests.test_halo.TstApi","Tst2":"tests.test_halo.Tst2Api","Tst3":"tests.test_halo.Tst3Api","Tst4":"tests.test_halo.Tst4Api"}

#ApiMngr.set_api_list(API_LIST)

class A0(AbsCommandHandler):
    repository = None
    domain_service = None
    infra_service = None

    def __init__(self):
        super(A0,self).__init__()
        self.repository = AbsRepository()
        self.domain_service = AbsDomainService()
        self.infra_service = AbsMailService()

    def handle(self,halo_request:HaloCommandRequest,uow:AbsUnitOfWork) ->Result:
        if 'id' in halo_request.command.vars:
            if halo_request.command.vars['id'] == '2':
                raise Exception("test2") # generic
            if halo_request.command.vars['id'] == '3':
                raise AbsInfraException("test3")# infra
            if halo_request.command.vars['id'] == '4':
                raise AbsDomainException("test4")# domain
            if halo_request.command.vars['id'] == '5':
                return Result.fail("code","msg","fail5")
            if halo_request.command.vars['id'] == '6':
                return Result.fail("code","msg","fail6",Exception("exc"))
            if halo_request.command.vars['id'] == '7':
                return Result.fail("code","msg","fail7",AbsDomainException("dom exc"))

        with uow:
            item = self.repository.load(halo_request.command.vars['id'])
            entity = self.domain_service.validate(item)
            self.infra_service.send(entity)
            uow.commit()
            payload = {"1": {"a": "b"}}
            return Result.ok(payload) #Util.create_response(halo_request, True, payload)

    def set_back_api(self,halo_request, foi=None):
        if not foi:#not in seq
            if halo_request.method_id == "z1" or halo_request.method_id == "z1a" or halo_request.method_id == "z5":
                return ApiMngr.get_api_instance("Cnn",halo_request.context,HTTPChoice.get.value)
                #return CnnApi(halo_request.context,HTTPChoice.delete.value)
        return None

    def extract_json(self,halo_request,api, back_response, seq=None):
        if seq == None:#no event
            if halo_request.method_id == "z1":
                return {"tst_get":"good"}
            if halo_request.method_id == "z1a":
                return {"tst_delete":"good"}
        else:#in event
            if halo_request.method_id == HTTPChoice.put.value:#method type
                if seq == '1':
                    return {"tst_put":"good1"}
                if seq == '2':
                    return {"tst_put":"good2"}
            if halo_request.method_id == HTTPChoice.post.value:#method type
                if seq == '1':
                    return {"tst_post":"good1"}
                if seq == '2':
                    return {"tst_post":"good2"}
            if halo_request.method_id == HTTPChoice.patch.value:#method type
                return {"tst_patch":"good"}
class A1(A0):
    pass

class A3(AbsCommandHandler):

    def do_filter(self, halo_request, halo_response):  #
        request_filter = self.get_request_filter(halo_request)
        request_filter.do_filter(halo_request, halo_response)

class A2(A1):

    def set_api_data(self,halo_request,api, seq=None, dict=None):
        if seq == '1':
            return {}
        if seq == '3':
            return {}
        ret = super(A2,self).set_api_data(halo_request,api, seq, dict)
        return ret

    def set_api_headers(self,halo_request,api, seq=None, dict=None):
        return super(A2,self).set_api_headers(halo_request,api, seq, dict)

    def set_api_vars(self,halo_request,api, seq=None, dict=None):
        return super(A2,self).set_api_vars(halo_request,api, seq, dict)

    def set_api_auth(self,halo_request,api, seq=None, dict=None):
        return super(A2,self).set_api_auth(halo_request,api, seq, dict)

    def set_api_data(self,halo_request,api, seq=None, dict=None):
        ret = super(A2,self).set_api_data(halo_request,api, seq, dict)
        return ret

    def execute_api(self,halo_request, back_api, back_vars, back_headers, back_auth, back_data=None, seq=None, dict=None):
        return super(A2,self).execute_api(halo_request, back_api, back_vars, back_headers, back_auth, back_data, seq, dict)

    def extract_json(self,halo_request,api, back_response, seq=None):
        if seq == None:#no event
            if halo_request.method_id == "z1":#method type
                return {"tst_get_deposit":"good"}
            else:
                return {"tst_delete_deposit":"good"}
        else:#in event
            if halo_request.method_id == "z1":#method type
                if seq == '1':
                    return {"tst_put_deposit":"good1"}
                if seq == '2':
                    return {"tst_put_deposit":"good2"}


    def create_resp_payload(self, halo_request, dict_back_json):
        if dict_back_json:
            dict_back_json = {
              "employees": [
                {
                  "id": 1,
                  "name": "Pankaj",
                  "salary": "10000"
                },
                {
                  "name": "David",
                  "salary": "5000",
                  "id": 2
                }
              ]
            }
            dict_back_json1 = {
	"store": {
		"book": [{
			"category": "reference",
			"author": "Nigel Rees",
			"title": "Sayings of the Century",
			"price": 8.95
		}, {
			"category": "fiction",
			"author": "Evelyn Waugh",
			"title": "Sword of Honour",
			"price": 12.99
		}, {
			"category": "fiction",
			"author": "Herman Melville",
			"title": "Moby Dick",
			"isbn": "0-553-21311-3",
			"price": 8.99
		}, {
			"category": "fiction",
			"author": "J. R. R. Tolkien",
			"title": "The Lord of the Rings",
			"isbn": "0-395-19395-8",
			"price": 22.99
		}],
		"bicycle": {
			"color": "red",
			"price": 19.95
		}
	},
	"expensive": 10
}
            return  super(A2,self).create_resp_payload(halo_request, dict_back_json)

    def create_response(self,halo_request, payload, headers):
        code = 200
        if halo_request.method_id == "z4" or halo_request.method_id == "z5" or halo_request.method_id == "z6":
            code = 500
        return HaloCommandResponse(halo_request, payload, code, headers)

class A4(A2):
    secure = True

class A5(AbsCommandHandler):
    secure = True

class A6(A5):
    pass

class A15a(AbsCommandHandler):
    def validate_req(self, halo_request):
        n = Notification()
        n.addError("test","valid test1")
        return n

class A15b(AbsCommandHandler):

    def validate_pre(self, halo_request):
        n = Notification()
        n.addError("test","valid test2")
        return n

class A8(AbsCommandHandler):
    pass

class A9(AbsEventHandler):

    def handle(self, halo_event_request: HaloEventRequest, uow: AbsUnitOfWork)->Result:
        if halo_event_request.event.xid != '12':
            print("exception:"+halo_event_request.event.xid)
            raise Exception("id not good")
        print("success:"+halo_event_request.event.xid)
        return Result.ok()

class A10(AbsQueryHandler):
    def set_query_data(self,halo_query_request: HaloQueryRequest):
        item_dtl_id = halo_query_request.query.vars['id']
        qty = halo_query_request.query.vars['qty']
        return 'SELECT desc,qty FROM items_view WHERE item_dtl_id=:item_dtl_id AND qty=:qty',dict(item_dtl_id=item_dtl_id, qty=qty)

class A11(AbsQueryHandler):
    def set_query_data(self,halo_query_request: HaloQueryRequest):
        orderid = 1
        sku = 2
        return 'SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku',dict(orderid=orderid, sku=sku)

@dataclass
class ItemDto(AbsHaloDto):
    id = None
    data = None

    def __init__(self,id=None,data=None):
        super(ItemDto, self).__init__()
        self.id = id
        self.data = data

class DtoMapper(AbsHaloDtoMapper):
    def __init__(self):
        super(DtoMapper, self).__init__()

    def map_to_dto(self,object,dto_class_type):
        self.mapper.create_map(object.__class__, dto_class_type)
        dto = self.mapper.map(object, dto_class_type)
        return dto


    def map_from_dto(self,AbsHaloDto,object):
        pass

class ItemAssembler(AbsDtoAssembler):
    def write_dto(self,entity:Item) -> ItemDto:
        dto = ItemDto("1",entity.data)
        return dto

    def write_entity(self,dto:ItemDto)->Item:
        entity = Item(dto.id,dto.data)
        return entity

    def write_dto_for_method(self, method_id: str,data:dict,flag:str=None) -> AbsHaloDto:
        if method_id == "z17" and flag:
            return ItemDto("1",data["i"])
        dto_mapper = DtoMapper()
        dto = dto_mapper.map_to_dto(data,ItemDto.__class__)
        return dto

class A17(A0):

    def handle(self,halo_request:HaloCommandRequest,uow:AbsUnitOfWork) ->Result:
        with uow:
            if 'id' in halo_request.command.vars:
                if halo_request.command.vars['id'] == '1':
                    entity = Item("1","123")
                    self.repository.save(entity)
                    self.infra_service.send(entity)
                    uow.commit()
                    dto_assembler = DtoAssemblerFactory.get_assembler_by_entity(entity)
                    dto = dto_assembler.write_dto(entity)
                    payload = dto
                    return Result.ok(payload)
                if halo_request.command.vars['id'] == '2':
                    dto = ItemDto("1","456")
                    dto_assembler = DtoAssemblerFactory.get_assembler_by_dto(dto)
                    entity = dto_assembler.write_entity(dto)
                    self.repository.save(entity)
                    uow.commit()
                    payload = dto
                    return Result.ok(payload)
                if halo_request.command.vars['id'] == '3':
                    dto_assembler = DtoAssemblerFactory.get_assembler_by_request(halo_request)
                    dto = dto_assembler.write_dto_for_method(halo_request.method_id,{"i":"789"},"x")
                    uow.commit()
                    payload = dto
                    return Result.ok(payload)
                if halo_request.command.vars['id'] == '4':
                    dto_assembler = DtoAssemblerFactory.get_assembler_by_request(halo_request)
                    dto = dto_assembler.write_dto_for_method(halo_request.method_id,{"id":"1","data":"789"})
                    uow.commit()
                    payload = dto
                    return Result.ok(payload)

                return Result.fail("code","msg","failx")

class TestHaloEvent(AbsHaloEvent):
    xid:str = None

    def __init__(self, ctx, mid, xid:str):
        super(TestHaloEvent, self).__init__(ctx, mid)
        self.xid = xid

class TestHaloQuery(HaloQuery):

    def __init__(self, ctx, name,vars):
        super(TestHaloQuery, self).__init__(ctx, name,vars)

from halo_app.app.anlytx_filter import RequestFilter,RequestFilterClear
class TestFilter(RequestFilter):
    def augment_event_with_headers_and_data(self,event, halo_request,halo_response):
        event.put(HaloContext.items.get(HaloContext.CORRELATION), halo_request.context.get(HaloContext.items.get(HaloContext.CORRELATION)))
        return event

class TestRequestFilterClear(RequestFilterClear):
    def run(self,event):
        print("insert_events_to_repository " + str(event.serialize()))

class TestAwsRequestFilterClear(RequestFilterClear):
    def run(self,event):
        from halo_app.infra.providers.providers import get_provider
        get_provider().publish()
        print("insert_events_to_repository " + str(event.serialize()))


class CAContext(HaloContext):
    TESTER = "TESTER"

    HaloContext.items[TESTER] = "x-tester-id"

def get_host_name():
    if 'HALO_HOST' in os.environ:
        return os.environ['HALO_HOST']
    else:
        return 'HALO_HOST'


class XClientType(ClientType):
    tester = 'TESTER'

class XHaloResponseFactory(HaloResponseFactory):

    def get_halo_response(self, halo_request: AbsHaloRequest, success: bool, payload) -> AbsHaloResponse:
        class TesterHaloResponse(HaloCommandResponse):
            pass
        if isinstance(halo_request, HaloCommandRequest) or issubclass(halo_request.__class__, HaloCommandRequest):
            return TesterHaloResponse(halo_request, success,payload)
        return super(XHaloResponseFactory,self).get_halo_response(halo_request,success, payload)

boundary = None

@pytest.fixture
def sqlite_boundary(sqlite_session_factory):
    from halo_app import bootstrap
    global boundary
    if boundary:
        return boundary
    boundary = bootstrap.bootstrap(
        start_orm=True,
        uow=SqlAlchemyUnitOfWork(sqlite_session_factory),
        publish=FakePublisher()
    )
    return boundary

class TestUserDetailTestCase(unittest.TestCase):
    """
    Tests /users detail operations.
    """

    @classmethod
    def setUpClass(cls):
        print(" do start")
        from halo_app.const import LOC
        app.config['ENV_TYPE'] = LOC
        app.config['SSM_TYPE'] = "AWS"
        app.config['PROVIDER'] = "AWS"
        app.config['FUNC_NAME'] = "FUNC_NAME"
        #app.config['API_CONFIG'] = None
        app.config['AWS_REGION'] = 'us-east-1'
        # config
        from halo_app import bootstrap
        bootstrap.COMMAND_HANDLERS["z0"] = A0.run_command_class  # simple handle + fail
        bootstrap.COMMAND_HANDLERS["z1"] = A1.run_command_class  # event 1 api
        bootstrap.COMMAND_HANDLERS["z1a"] = A1.run_command_class  # event empty api
        bootstrap.COMMAND_HANDLERS["z1b"] = A1.run_command_class  # event seq api
        bootstrap.COMMAND_HANDLERS["z1c"] = A1.run_command_class  # event saga api
        bootstrap.COMMAND_HANDLERS["z2"] = A8.run_command_class
        bootstrap.COMMAND_HANDLERS["z8"] = A8.run_command_class
        bootstrap.COMMAND_HANDLERS["z3"] = A3.run_command_class
        # bootstrap.COMMAND_HANDLERS["z7"] = A7.run_command_class
        bootstrap.COMMAND_HANDLERS["z4"] = A2.run_command_class
        bootstrap.COMMAND_HANDLERS["z5"] = A2.run_command_class
        bootstrap.COMMAND_HANDLERS["z6"] = A2.run_command_class
        bootstrap.COMMAND_HANDLERS["z15"] = A15a.run_command_class
        bootstrap.COMMAND_HANDLERS["z16"] = A15b.run_command_class
        bootstrap.COMMAND_HANDLERS["z17"] = A17.run_command_class
        bootstrap.EVENT_HANDLERS[TestHaloEvent] = [A9.run_event_class]
        bootstrap.QUERY_HANDLERS["q1"] = A10.run_query_class
        bootstrap.QUERY_HANDLERS["q2"] = A11.run_query_class

    def setUp(self):
        #self.app = app#.test_client()
        #app.config.from_pyfile('../settings.py')
        app.config.from_object(f"halo_app.config.Config_{os.getenv('HALO_STAGE', 'loc')}")
        #from halo_app.settingsx import settingsx
        #settings = settingsx()
        with app.test_request_context(method='GET', path='/?abc=def'):
            try:
                load_api_config(app.config['ENV_TYPE'], app.config['SSM_TYPE'], app.config['FUNC_NAME'],
                                app.config['API_CONFIG'])
            except Exception as e:
                eq_(e.__class__.__name__, "NoApiClassException")
        print("do setup")

    @pytest.fixture(autouse=True)
    def init_boundary(self, sqlite_boundary):
        self.boundary = sqlite_boundary


    def test_000_start(self):
        from halo_app.const import LOC
        app.config['ENV_TYPE'] = LOC
        app.config['SSM_TYPE'] = "AWS"
        app.config['FUNC_NAME'] = "FUNC_NAME"
        #app.config['API_CONFIG'] =
        app.config['AWS_REGION'] = 'us-east-1'
        with app.test_request_context(method='GET', path='/?abc=def'):
            try:
                load_api_config(app.config['ENV_TYPE'], app.config['SSM_TYPE'], app.config['FUNC_NAME'],
                                app.config['API_CONFIG'])
            except Exception as e:
                eq_(e.__class__.__name__, "NoApiClassException")

    def test_00_start(self):
        app.config['SSM_TYPE'] = "AWS"
        app.config['AWS_REGION'] = 'us-east-1'
        with app.test_request_context(method='GET', path='/?abc=def'):
            try:
                HALO_HOST = get_host_name()
                params = {}
                params["url"] = set_host_param_config(HALO_HOST)
                set_app_param_config(app.config['SSM_TYPE'],params)
            except Exception as e:
                eq_(e.__class__.__name__, "NoApiClassException")

    def test_01_start(self):
        app.config['SSM_TYPE'] = "AWS"
        app.config['AWS_REGION'] = 'us-east-1'
        app.config['FUNC_NAME'] = "halo_app"
        with app.test_request_context(method='GET', path='/?abc=def'):
            try:
                val = get_app_param_config(app.config['SSM_TYPE'], app.config['FUNC_NAME'],"url")
                print("get_app_param_config="+str(val))
            except Exception as e:
                eq_(e.__class__.__name__, "NoApiClassException")

    def test_0_start(self):
        with app.test_request_context(method='GET', path='/?abc=def'):
            try:
                if 'INIT_DATA_MAP' in app.config and 'INIT_CLASS_NAME' in app.config:
                    data_map = app.config['INIT_DATA_MAP']
                    class_name = app.config['INIT_CLASS_NAME']
                    load_global_data(class_name, data_map)
            except Exception as e:
                eq_(e.__class__.__name__, "NoApiClassException")

    def test_1_run_handle(self):
        with app.test_request_context(method='GET', path='/?id=1'):
            try:
                halo_context = client_util.get_halo_context(request.headers)
                halo_request = SysUtil.create_command_request(halo_context, "z0", request.args)
                response = self.boundary.execute(halo_request)
                eq_(response.success,True)
                eq_(response.payload['1'], {'a': 'b'})
            except Exception as e:
                print(str(e))
                eq_(e.__class__.__name__, "NoApiClassException")

    def test_1a_run_query(self):
        #app.config['UOW_CLASS'] = "halo_app.infra.fake.FakeUnitOfWork"
        #app.config['PUBLISHER_CLASS'] = "halo_app.infra.fake.FakePublisher"
        with app.test_request_context(method='GET', path='/?id=1&qty=2'):
            try:
                halo_context = client_util.get_halo_context(request.headers)
                t = TestHaloQuery(halo_context, "q1",  request.args)
                halo_request = SysUtil.create_query_request(t)
                response = self.boundary.execute(halo_request)
                eq_(response.success,True)
                eq_(response.payload, {})
            except Exception as e:
                print(str(e))
                eq_(e.__class__.__name__, "NoApiClassException")

    def test_1b_run_query_error(self):
        #app.config['UOW_CLASS'] = "halo_app.infra.fake.FakeUnitOfWork"
        #app.config['PUBLISHER_CLASS'] = "halo_app.infra.fake.FakePublisher"
        with app.test_request_context(method='GET', path='/?id=1'):
            try:
                halo_context = client_util.get_halo_context(request.headers)
                t = TestHaloQuery(halo_context, "q2",  request.args)
                halo_request = SysUtil.create_query_request(t)
                response = self.boundary.execute(halo_request)
                response = SysUtil.process_response_for_client(response, request.method)
                eq_(response.success,False)
            except Exception as e:
                print(str(e))
                eq_(e.__class__.__name__, "NoApiClassException")

    def test_1c_run_handle_async(self):
        app.config['ASYNC_MODE'] = True
        with app.test_request_context(method='GET', path='/?id=1'):
            try:
                halo_context = client_util.get_halo_context(request.headers)
                halo_request = SysUtil.create_command_request(halo_context, "z0", request.args)
                response = self.boundary.execute(halo_request)
                response = SysUtil.process_response_for_client(response, request.method)
                eq_(response.success,True)
                eq_(response.code, HTTPStatus.ACCEPTED)
            except Exception as e:
                print(str(e))
                eq_(e.__class__.__name__, "NoApiClassException")

    def test_1d_run_handle_async(self):
        event_consumer = FakeConsumer()
        try:
            event_consumer.handle_command({'data':'{"method_id":"z0","id":"1"}'})
        except Exception as e:
            print(str(e))
            eq_(e.__class__.__name__, "NoApiClassException")

    def test_1e_fail_valid(self):
        with app.test_request_context(method='GET', path='/?id=1'):
            try:
                halo_context = client_util.get_halo_context(request.headers)
                halo_request = SysUtil.create_command_request(halo_context, "z15", request.args)
                response = self.boundary.execute(halo_request)
                response = SysUtil.process_response_for_client(response, request.method)
                eq_(response.success, False)
                eq_(response.error['error_code'], 'validation')
            except Exception as e:
                print(str(e))
                eq_(e.__class__.__name__, "NoApiClassException")

    def test_1f_fail_valid(self):
        with app.test_request_context(method='GET', path='/?id=1'):
            try:
                halo_context = client_util.get_halo_context(request.headers)
                halo_request = SysUtil.create_command_request(halo_context, "z16", request.args)
                response = self.boundary.execute(halo_request)
                response = SysUtil.process_response_for_client(response, request.method)
                eq_(response.success,False)
                eq_(response.error['error_code'], 'validation')
            except Exception as e:
                print(str(e))
                eq_(e.__class__.__name__, "NoApiClassException")


    def test_2_run_handle_fail_exception(self):
        with app.test_request_context(method='GET', path='/?id=2'):
            try:
                halo_context = client_util.get_halo_context(request.headers)
                halo_request = SysUtil.create_command_request(halo_context, "z0", request.args)
                response = self.boundary.execute(halo_request)
                response = SysUtil.process_response_for_client(response, request.method)
                print(str(response.payload))
                eq_(response.success,False)
                eq_(response.error['error']['error_message'], 'test2')
            except Exception as e:
                print(str(e))
                eq_(e.__class__.__name__, "Exception")

    def test_2a_run_handle_fail_result(self):
        with app.test_request_context(method='GET', path='/?id=3'):
            try:
                halo_context = client_util.get_halo_context(request.headers)
                halo_request = SysUtil.create_command_request(halo_context, "z0", request.args)
                response = self.boundary.execute(halo_request)
                response = SysUtil.process_response_for_client(response, request.method)
                print(str(response.payload))
                eq_(response.success,False)
                eq_(response.error['error']['error_message'], 'test3')
            except Exception as e:
                print(str(e))
                eq_(e.__class__.__name__, "Exception")

    def test_2b_run_handle_fail_result(self):
        with app.test_request_context(method='GET', path='/?id=4'):
            try:
                halo_context = client_util.get_halo_context(request.headers)
                halo_request = SysUtil.create_command_request(halo_context, "z0", request.args)
                response = self.boundary.execute(halo_request)
                response = SysUtil.process_response_for_client(response, request.method)
                print(str(response.payload))
                eq_(response.success,False)
                eq_(response.error['error']['error_message'], 'test4 ,original:test4')
            except Exception as e:
                print(str(e))
                eq_(e.__class__.__name__, "Exception")

    def test_2c_run_handle_fail_result(self):
        with app.test_request_context(method='GET', path='/?id=5'):
            try:
                halo_context = client_util.get_halo_context(request.headers)
                halo_request = SysUtil.create_command_request(halo_context, "z0", request.args)
                response = self.boundary.execute(halo_request)
                response = SysUtil.process_response_for_client(response, request.method)
                print(str(response.payload))
                eq_(response.success,False)
                eq_(response.error.errors[0].message, 'fail5')
            except Exception as e:
                print(str(e))
                eq_(e.__class__.__name__, "Exception")

    def test_2d_run_handle_fail_result(self):
        with app.test_request_context(method='GET', path='/?id=6'):
            try:
                halo_context = client_util.get_halo_context(request.headers)
                halo_request = SysUtil.create_command_request(halo_context, "z0", request.args)
                response = self.boundary.execute(halo_request)
                response = SysUtil.process_response_for_client(response, request.method)
                print(str(response.payload))
                eq_(response.success,False)
                eq_(response.error.errors[0].message, 'fail6')
            except Exception as e:
                print(str(e))
                eq_(e.__class__.__name__, "Exception")

    def test_2e_run_handle_fail_result(self):
        with app.test_request_context(method='GET', path='/?id=7'):
            try:
                halo_context = client_util.get_halo_context(request.headers)
                halo_request = SysUtil.create_command_request(halo_context, "z0", request.args)
                response = self.boundary.execute(halo_request)
                response = SysUtil.process_response_for_client(response, request.method)
                print(str(response.payload))
                eq_(response.success,False)
                eq_(response.error.errors[0].message, 'fail7')
            except Exception as e:
                print(str(e))
                eq_(e.__class__.__name__, "Exception")

    def test_2f_run_api_from_event_config(self):
        os.environ['DEBUG_LOG'] = 'true'
        with app.test_request_context(method='GET', path='/?id=1'):
            try:
                halo_context = client_util.get_halo_context(request.headers)
                halo_request = SysUtil.create_command_request(halo_context, "z1", request.args)
                response = self.boundary.execute(halo_request)
                response = SysUtil.process_response_for_client(response, request.method)
                print(str(response.payload))
                eq_(response.success,True)
            except Exception as e:
                print(str(e))
                eq_(e.__class__.__name__, "NoApiClassException")

    def test_2g_run_api_from_event_config_empty(self):
        os.environ['DEBUG_LOG'] = 'true'
        with app.test_request_context(method='GET', path='/?id=1'):
            try:
                halo_context = client_util.get_halo_context(request.headers)
                halo_request = SysUtil.create_command_request(halo_context, "z1a", request.args)
                response = self.boundary.execute(halo_request)
                response = SysUtil.process_response_for_client(response, request.method)
                print(str(response.payload))
                eq_(response.success,True)
            except Exception as e:
                print(str(e))
                eq_(e.__class__.__name__, "NoApiClassException")

    def test_3_run_seq(self):
        os.environ['DEBUG_LOG'] = 'true'
        with app.test_request_context(method='DELETE', path='/'):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z1b", request.args)
            response = self.boundary.execute(halo_request)
            response = SysUtil.process_response_for_client(response, request.method)
            print(str(response.payload))
            eq_(response.success,True)

    def test_4_run_saga(self):
        with app.test_request_context(method='PUT', path='/?abc=def'):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z1c", {})
            response = self.boundary.execute(halo_request)
            response = SysUtil.process_response_for_client(response, request.method)
            eq_(response.success,True)

    def test_5_cli_handle(self):
        halo_context = client_util.get_halo_context({},client_type=ClientType.cli)
        halo_request = SysUtil.create_command_request(halo_context, "z0", {"id": "1"})
        response = self.boundary.execute(halo_request)
        eq_(response.success,True)

    def test_5a_cli_handle(self):
        from halo_app.settingsx import settingsx
        settings = settingsx()
        print(settings.HALO_CLIENT_CLASS)
        client_type_ins = Util.get_client_type()
        client_type = client_type_ins.cli
        halo_context = client_util.get_halo_context({},client_type=client_type)
        halo_request = SysUtil.create_command_request(halo_context, "z0", {"id": "1"})
        response = self.boundary.execute(halo_request)
        eq_(response.success,True)

    def test_6_cli_handle_with_event(self):
        halo_context = client_util.get_halo_context({},client_type=ClientType.cli)
        halo_request = SysUtil.create_command_request(halo_context, "z0", {"id": "1"})
        response = self.boundary.execute(halo_request)
        eq_(response.success,True)

    def test_7_cli_api_from_config(self):
        halo_context = client_util.get_halo_context({},client_type=ClientType.cli)
        halo_request = SysUtil.create_command_request(halo_context, "z1", {"id": "1"})
        response = self.boundary.execute(halo_request)
        eq_(response.success,True)

    def test_7a_cli_api_from_method(self):
        halo_context = client_util.get_halo_context({},client_type=ClientType.cli)
        halo_request = SysUtil.create_command_request(halo_context, "z1a", {"id": "1"})
        response = self.boundary.execute(halo_request)
        eq_(response.success,True)

    def test_8_cli_seq(self):
        halo_context = client_util.get_halo_context({},client_type=ClientType.cli)
        halo_request = SysUtil.create_command_request(halo_context, "z8", {})
        response = self.boundary.execute(halo_request)
        eq_(response.success,True)

    def test_9_cli_saga(self):
        halo_context = client_util.get_halo_context({},client_type=ClientType.cli)
        halo_request = SysUtil.create_command_request(halo_context, "z3", {})
        response = self.boundary.execute(halo_request)
        eq_(response.success,True)

    def test_9a_cli_query(self):
        halo_context = client_util.get_halo_context({},client_type=ClientType.cli)
        t = TestHaloQuery(halo_context,"q1",{'id':1,'qty':2})
        halo_request = SysUtil.create_query_request(t)
        response = self.boundary.execute(halo_request)
        eq_(response.success, True)
        eq_(response.payload,{})

    def test_9b_cli_query_error(self):
        halo_context = client_util.get_halo_context({},client_type=ClientType.cli)
        t = TestHaloQuery(halo_context, "q2", {})
        halo_request = SysUtil.create_query_request(t)
        response = self.boundary.execute(halo_request)
        eq_(response.success,False)
        eq_(response.error.message, 'exception thrown!')

    def test_10_event(self):
        halo_context = client_util.get_halo_context({},client_type=ClientType.cli)
        halo_event = TestHaloEvent(halo_context, "z9","12")
        halo_request = SysUtil.create_event_request(halo_event)
        fake_boundary = FakeBoundary(self.boundary.uow,self.boundary.publisher,self.boundary.event_handlers,self.boundary.command_handlers,self.boundary.query_handlers)
        fake_boundary.fake_process(halo_request)

    def test_10a_event(self):
        with app.test_request_context(method='GET', path='/?a=b'):
            halo_context = client_util.get_halo_context(request.headers)
            halo_event = TestHaloEvent(halo_context, "z9", "12")
            halo_request = SysUtil.create_event_request(halo_event)
            fake_boundary = FakeBoundary(self.boundary.uow,self.boundary.publisher, self.boundary.event_handlers, self.boundary.command_handlers,
                                        self.boundary.query_handlers)
            fake_boundary.fake_process(halo_request)


    def test_11_api_request(self):
        app.config['PROVIDER'] = "AWS"
        with app.test_request_context(method='GET', path='/?a=b'):
            halo_context = client_util.get_halo_context(request.headers)
            api = TstApi(halo_context)
            from halo_app.app.utilx import Util
            timeout = Util.get_timeout(halo_context)
            try:
                response = api.get(timeout)
            except ApiException as e:
                pass
            try:
                response = api.get(timeout)
            except ApiException as e:
                pass
            try:
                response = api.get(timeout)
            except ApiException as e:
                pass
            try:
                response = api.get(timeout)
            except ApiException as e:
                print(str(e))
                eq_(e.__class__.__name__, "ApiException")

    def test_12_api_request(self):
        app.config['PROVIDER'] = "AWS"
        #self.test_6_api_request_returns_a_CircuitBreakerError()
        with app.test_request_context(method='GET', path='/?a=b'):
            halo_context = client_util.get_halo_context(request.headers)
            api = TstApi(halo_context)
            timeout = Util.get_timeout(halo_context)
            try:
                response = api.get(timeout)
            except Exception as e:
                print(str(e))
            try:
                response = api.get(timeout)
            except Exception as e:
                print(str(e))
            try:
                response = api.get(timeout)
            except Exception as e:
                print(str(e))
            try:
                response = api.get(timeout)
            except Exception as e:
                print(str(e))
            api = CnnApi(halo_context)
            timeout = Util.get_timeout(halo_context)
            try:
                response = api.get(timeout)
                eq_(response.status_code, HTTPStatus.OK)
            except ApiException as e:
                eq_(1,2)

    def test_13_api_request_returns_a_fail(self):
        with app.test_request_context(method='GET', path='/?a=b'):
            halo_context = client_util.get_halo_context(request.headers)
            api = CnnApi(halo_context)
            api.url = api.url + "/lgkmlgkhm??l,mhb&&,g,hj "
            timeout = Util.get_timeout(halo_context)
            try:
                response = api.get(timeout)
                assert False
            except ApiException as e:
                eq_(e.status_code, HTTPStatus.NOT_FOUND)
                #eq_(e.__class__.__name__,"CircuitBreakerError")

    def test_14_api_request_soap(self):
        with app.test_request_context(method='GET', path='/'):
            halo_context = client_util.get_halo_context(request.headers)
            api = Tst2Api(halo_context,method='method1')
            timeout = Util.get_timeout(halo_context)
            try:
                data = {}
                data['first'] = 'start'
                data['second'] = 'end'
                response = api.run(timeout,data)
                print("response=" + str(response.content))
                eq_(json.loads(response.content)['msg'],'Your input parameters are start and end')
            except ApiException as e:
                #eq_(e.status_code, status.HTTP_404_NOT_FOUND)
                eq_(response.payload['first'],'start')

    def test_15_api_request_soap_returns(self):
        with app.test_request_context(method='GET', path='/'):
            halo_context = client_util.get_halo_context(request.headers)
            api = Tst2Api(halo_context,method='method1')
            timeout = Util.get_timeout(halo_context)
            try:
                data = {}
                data['first'] = 'start'
                data['second'] = 'end'
                response = api.run(timeout,data)
                print("response=" + str(response.content))
                eq_(json.loads(response.content)['msg'],'Your input parameters are start and end')
            except HaloMethodNotImplementedException as e:
                #eq_(e.status_code, status.HTTP_404_NOT_FOUND)
                eq_(e.__class__.__name__,"HaloMethodNotImplementedException")

    def test_16_api_request_rpc_returns(self):
        app.config['PROVIDER'] = "AWS"
        with app.test_request_context(method='GET', path='/?a=b'):
            halo_context = client_util.get_halo_context(request.headers)
            api = Tst3Api(halo_context)
            timeout = Util.get_timeout(halo_context)
            try:
                response = api.get(timeout)
                assert False
            except ApiException as e:
                #eq_(e.status_code, status.HTTP_404_NOT_FOUND)
                eq_(e.__class__.__name__,"ApiException")

    def test_17_api_request_event_returns(self):
        app.config['PROVIDER'] = "AWS"
        with app.test_request_context(method='GET', path='/?a=b'):
            halo_context = client_util.get_halo_context(request.headers)
            api = Tst4Api(halo_context)
            timeout = Util.get_timeout(halo_context)
            try:
                response = api.get(timeout)
                assert False
            except ApiException as e:
                eq_(e.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
                #eq_(e.__class__.__name__,"CircuitBreakerError")

    def test_18_send_event(self):
        with app.test_request_context(method='GET', path='/?a=b'):
            from halo_app.events import AbsBaseEvent
            class Event1Event(AbsBaseEvent):
                target_service = 'func1'
                key_name = 'def'
                key_val = '456'

            event = Event1Event()
            dict = {"name": "david"}
            response = event.send_event(dict)
            print("event response " + str(response))
            eq_(response, 'sent event')

    def test_19_event_filter(self):
        app.config['SSM_TYPE'] = "AWS"
        app.config['AWS_REGION'] = 'us-east-1'
        app.config['PROVIDER'] = "AWS"
        app.config['REQUEST_FILTER_CLASS'] = 'tests.test_halo.TestFilter'
        with app.test_request_context(method='POST', path='/?id=b',headers= {HaloContext.items.get(HaloContext.CORRELATION):"123"},data={"a":"1"}):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z1", request.args)
            response = self.boundary.execute(halo_request)
            eq_(response.payload, [{'id': 1, 'name': 'Pankaj', 'salary': '10000'}, {'name': 'David', 'salary': '5000', 'id': 2}])

    def test_20_event_filter(self):
        app.config['PROVIDER'] = "AWS"
        app.config['REQUEST_FILTER_CLASS'] = 'tests.test_halo.TestFilter'
        with app.test_request_context(method='GET', path='/?id=b',headers= {HaloContext.items.get(HaloContext.CORRELATION):"123"}):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z1", request.args)
            response = self.boundary.execute(halo_request)
            eq_(response.payload, [{'id': 1, 'name': 'Pankaj', 'salary': '10000'}, {'name': 'David', 'salary': '5000', 'id': 2}])

    def test_21_event_filter(self):
        app.config['PROVIDER'] = "AWS"
        app.config['REQUEST_FILTER_CLASS'] = 'tests.test_halo.TestFilter'
        app.config['REQUEST_FILTER_CLEAR_CLASS'] = 'tests.test_halo.TestRequestFilterClear'
        with app.test_request_context(method='GET', path='/?id=b',headers= {HaloContext.items.get(HaloContext.CORRELATION):"123"}):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z1", request.args)
            response = self.boundary.execute(halo_request)

    def test_22_event_filter(self):
        app.config['PROVIDER'] = "AWS"
        app.config['REQUEST_FILTER_CLASS'] = 'tests.test_halo.TestFilter'
        app.config['REQUEST_FILTER_CLEAR_CLASS'] = 'tests.test_halo.TestRequestFilterClear'
        with app.test_request_context(method='GET', path='/?id=b',headers= {HaloContext.items.get(HaloContext.CORRELATION):"123"}):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z1", request.args)
            response = self.boundary.execute(halo_request)

    def test_23_event_filter(self):
        app.config['PROVIDER'] = "AWS"
        app.config['REQUEST_FILTER_CLASS'] = 'tests.test_halo.TestFilter'
        app.config['REQUEST_FILTER_CLEAR_CLASS'] = 'tests.test_halo.TestAwsRequestFilterClear'
        with app.test_request_context(method='GET', path='/?id=b',headers= {HaloContext.items.get(HaloContext.CORRELATION):"123"}):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z10", request.args)
            response = self.boundary.execute(halo_request)

    def test_24_filter(self):
        app.config['PROVIDER'] = "AWS"
        app.config['REQUEST_FILTER_CLASS'] = 'tests.test_halo.TestFilter'
        app.config['REQUEST_FILTER_CLEAR_CLASS'] = 'tests.test_halo.TestAwsRequestFilterClear'
        with app.test_request_context(method='GET', path='/?a=b&q={"field": "weight", "op": "<", "value": 10.24}',headers= {HaloContext.items.get(HaloContext.CORRELATION):"123"}):
            q = request.args['q']
            import json
            from flask_filter.schemas import FilterSchema
            filter_schema = FilterSchema()
            try:
                collection_filter_json = json.loads(q)
                if "field" in collection_filter_json:
                    many = False
                else:
                    many = True
                filters = filter_schema.load(collection_filter_json, many=many)
                if not many:
                    filters = [filters]
                from halo_app.app.query_filters import Filter
                arr = []
                for f in filters:
                    filter = Filter(f.field, f.OP, f.value)
                    arr.append(filter)

            except Exception as e:
                raise e

    def test_25_filter(self):
        app.config['PROVIDER'] = "AWS"
        app.config['REQUEST_FILTER_CLASS'] = 'tests.test_halo.TestFilter'
        app.config['REQUEST_FILTER_CLEAR_CLASS'] = 'tests.test_halo.TestAwsRequestFilterClear'
        with app.test_request_context(method='GET', path='/?a=b&q={"field": "weight", "op": "?", "value": 10.24}',headers= {HaloContext.items.get(HaloContext.CORRELATION):"123"}):
            q = request.args['q']
            import json
            from flask_filter.schemas import FilterSchema
            filter_schema = FilterSchema()
            try:
                collection_filter_json = json.loads(q)
                if "field" in collection_filter_json:
                    many = False
                else:
                    many = True
                filters = filter_schema.load(collection_filter_json, many=many)
                if not many:
                    filters = [filters]
                from halo_app.app.query_filters import Filter
                arr = []
                for f in filters:
                    filter = Filter(f.field, f.OP, f.value)
                    arr.append(filter)

            except Exception as e:
                eq_(e.__class__.__name__, "ValidationError")

    def test_26_filter(self):
        app.config['PROVIDER'] = "AWS"
        app.config['REQUEST_FILTER_CLASS'] = 'tests.test_halo.TestFilter'
        app.config['REQUEST_FILTER_CLEAR_CLASS'] = 'tests.test_halo.TestAwsRequestFilterClear'
        with app.test_request_context(method='GET', path='/?a=b&q={"field": "weight", "op": ">", "value": 10.24}',headers= {HaloContext.items.get(HaloContext.CORRELATION):"123"}):
            q = request.args['q']
            import json
            from flask_filter.schemas import FilterSchema
            filter_schema = FilterSchema()
            try:
                collection_filter_json = json.loads(q)
                if "field" in collection_filter_json:
                    many = False
                else:
                    many = True
                filters = filter_schema.load(collection_filter_json, many=many)
                if not many:
                    filters = [filters]
                from halo_app.app.query_filters import Filter
                arr = []
                for f in filters:
                    filter = Filter(f.field, f.OP, f.value)
                    arr.append(filter)
                for f in arr:
                    if f.field == "weight":
                        eq_(True,f.apply(11))

            except Exception as e:
                eq_(e.__class__.__name__, "ValidationError")

    def test_27_filter(self):
        app.config['PROVIDER'] = "AWS"
        app.config['REQUEST_FILTER_CLASS'] = 'tests.test_halo.TestFilter'
        app.config['REQUEST_FILTER_CLEAR_CLASS'] = 'tests.test_halo.TestAwsRequestFilterClear'
        with app.test_request_context(method='GET', path='/?a=b&q={"field": "weight", "op": ">", "value": 10.24}',headers= {HaloContext.items.get(HaloContext.CORRELATION):"123"}):
            q = request.args['q']
            import json
            from flask_filter.schemas import FilterSchema
            filter_schema = FilterSchema()
            try:
                collection_filter_json = json.loads(q)
                if "field" in collection_filter_json:
                    many = False
                else:
                    many = True
                filters = filter_schema.load(collection_filter_json, many=many)
                if not many:
                    filters = [filters]
                from halo_app.app.query_filters import Filter
                arr = []
                for f in filters:
                    filter = Filter(f.field, f.OP, f.value)
                    arr.append(filter)
                for f in arr:
                    if f.field == "weight":
                        eq_(False,f.apply(10))

            except Exception as e:
                eq_(e.__class__.__name__, "ValidationError")

    def test_28_system_debug_enabled(self):
        with app.test_request_context(method='GET', path='/?a=b'):
            os.environ['DEBUG_LOG'] = 'true'
            flag = 'false'
            for i in range(0, 180):
                ret = Util.get_system_debug_enabled()
                print(ret)
                if ret == 'true':
                    flag = ret
            eq_(flag, 'true')

    def test_29_debug_enabled(self):
        app.config['PROVIDER'] = "AWS"
        #headers = {'HTTP_X_HALO_DEBUG_LOG_ENABLED': 'true'}
        headers = {'X-Halo-Debug-Log-Enabled': 'true'}
        with app.test_request_context(method='GET', path='/?a=b', headers=headers):
            ctx = client_util.get_halo_context(request.headers)
            print("x1:"+HaloContext.items[HaloContext.DEBUG_LOG])
            print("x2:"+str(ctx.table))
            eq_(ctx.table[HaloContext.DEBUG_LOG], 'true')

    def test_30_json_log(self):
        import traceback
        app.config['PROVIDER'] = "AWS"
        #headers = {'HTTP_X_HALO_DEBUG_LOG_ENABLED': 'true'}
        headers = {'x-halo-debug-log-enabled': 'true'}
        with app.test_request_context(method='GET', path='/?a=b', headers=headers):
            halo_context = client_util.get_halo_context(request.headers)
            try:
                raise Exception("test it")
            except Exception as e:
                e.stack = traceback.format_exc()
                ret = log_json(halo_context, {"abc": "def"}, err=e)
                print(str(ret))
                eq_(ret[HaloContext.DEBUG_LOG], 'true')

    def test_31_get_request_with_debug(self):
        app.config['PROVIDER'] = 'ONPREM'
        headers = {'x-halo-debug-log-enabled': 'true'}
        with app.test_request_context(method='GET', path='/?a=b', headers=headers):
            halo_context = client_util.get_halo_context(request.headers)
            ret = Util.isDebugEnabled(halo_context)
            eq_(ret, True)

    def test_32_debug_event(self):
        event = {HaloContext.items[HaloContext.DEBUG_LOG]: 'true'}
        ret = BaseUtil.get_correlation_from_event(event)
        eq_(BaseUtil.event_req_context[HaloContext.items[HaloContext.DEBUG_LOG]], 'true')
        ret = BaseUtil.get_correlation_from_event(event)
        eq_(ret[HaloContext.items[HaloContext.DEBUG_LOG]], 'true')

    def test_33_trans_json(self):
        with app.test_request_context(method='GET', path="/tst"):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z5", request.args)
            try:
                response = self.boundary.execute(halo_request)
                eq_(response.payload['1'], {})
            except Exception as e:
                eq_(e.__class__.__name__, "InternalServerError")

    # saga load + errors ###########

    def test_34_load_saga(self):
        with app.test_request_context(method='POST', path="/"):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z1", request.args)
            with open("../env/config/saga.json") as f:
                jsonx = json.load(f)
            sagax = saga.load_saga("test saga",halo_request, jsonx, app.config['SAGA_SCHEMA'])
            eq_(len(sagax.actions), 6)

    def test_35_run_saga_error(self):
        with app.test_request_context(method='POST', path="/tst?sub_func=tst"):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z4", request.args)
            try:
                response = self.boundary.execute(halo_request)
                response = SysUtil.process_response_for_client(response, request.method)
                eq_(response.success,False)
            except Exception as e:
                eq_(e.__class__.__name__, "InternalServerError")

    def test_36_rollback_saga(self):
        with app.test_request_context(method='PUT', path="/"):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z5", request.args)
            try:
                response = self.boundary.execute(halo_request)
                response = SysUtil.process_response_for_client(response, request.method)
                eq_(response.success,False)
            except Exception as e:
                eq_(e.__class__.__name__, "ApiException")

    def test_37_rollback_saga_error(self):
        with app.test_request_context(method='PATCH', path="/"):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z6", request.args)
            try:
                response = self.boundary.execute(halo_request)
                response = SysUtil.process_response_for_client(response, request.method)
                eq_(response.success,False)
            except Exception as e:
                eq_(e.__class__.__name__, "SagaError")

    # finish saga

    def test_38_ssm_aws(self):  # @TODO test without HALO_AWS
        header = {'HTTP_HOST': '127.0.0.2'}
        app.config['HALO_HOST'] = 'halo_app'
        app.config['SSM_TYPE'] = "AWS"
        #app.config['PROVIDER'] = "AWS"
        app.config['AWS_REGION'] = 'us-east-1'
        with app.test_request_context(method='GET', path='/?a=b', headers=header):
            halo_context = client_util.get_halo_context(request.headers)
            try:
                from halo_app.ssm import set_app_param_config
                params = {}
                params["id"] = "124"
                set_app_param_config(app.config['SSM_TYPE'],params )
                import time
                print("sleep.")
                time.sleep(5.4)
                from halo_app.ssm import get_app_config
                config = get_app_config(app.config['SSM_TYPE'])
                eq_(config.get_param("halo_app")["id"], '124')
            except Exception as e:
                eq_(e.__class__.__name__, "ProviderException")

    def test_39_ssm_aws(self):  # @TODO test with HALO_AWS
        header = {'HTTP_HOST': '127.0.0.2'}
        app.config['HALO_HOST'] = 'halo_app'
        app.config['SSM_TYPE'] = "AWS"
        app.config['PROVIDER'] = "AWS"
        app.config['AWS_REGION'] = 'us-east-1'
        with app.test_request_context(method='GET', path='/?a=b', headers=header):
            from halo_app.ssm import set_app_param_config,set_host_param_config
            params = {}
            params["url"] = set_host_param_config("127.0.0.1:8000")
            set_app_param_config(app.config['SSM_TYPE'], params)
            import time
            print("sleep.")
            time.sleep(5.4)
            from halo_app.ssm import get_app_config
            config = get_app_config(app.config['SSM_TYPE'])
            eq_(config.get_param("halo_app")["url"], 'https://127.0.0.1:8000/loc')

    def test_40_ssm_aws(self):  # @TODO test with HALO_AWS
        header = {'HTTP_HOST': '127.0.0.2'}
        app.config['HALO_HOST'] = 'halo_app'
        app.config['SSM_TYPE'] = "AWS"
        app.config['PROVIDER'] = "AWS"
        app.config['AWS_REGION'] = 'us-east-1'
        with app.test_request_context(method='GET', path='/?a=b', headers=header):
            from halo_app.ssm import set_app_param_config
            import uuid
            uuidx = uuid.uuid4().__str__()
            print(uuidx)
            params = {}
            params["session_id"] = uuidx
            set_app_param_config(app.config['SSM_TYPE'], params)
            import time
            print("sleep.")
            time.sleep(5.4)
            from halo_app.ssm import get_app_config
            config = get_app_config(app.config['SSM_TYPE'])
            eq_(config.get_param(app.config['HALO_HOST'])["session_id"], uuidx)

    def test_41_ssm_aws(self):  # @TODO test with HALO_AWS
        header = {'HTTP_HOST': '127.0.0.2'}
        app.config['HALO_HOST'] = 'halo_app'
        app.config['SSM_TYPE'] = None
        #app.config['PROVIDER'] = "AWS"
        #app.config['AWS_REGION'] = 'us-east-1'
        with app.test_request_context(method='GET', path='/?a=b', headers=header):
            try:
                from halo_app.ssm import set_app_param_config
                from halo_app.ssm import set_host_param_config
                params = {}
                params["url"] = set_host_param_config("halo_app:8000")
                set_app_param_config(app.config['SSM_TYPE'], params)
                import time
                print("sleep.")
                time.sleep(5.4)
                from halo_app.ssm import get_app_config
                config = get_app_config(app.config['SSM_TYPE'])
                eq_(config.get_param(app.config['HALO_HOST'])["url"], 'https://127.0.0.1:8000/loc')
            except Exception as e:
                eq_(e.__class__.__name__, "NoSSMDefinedException")

    def test_42_ssm_aws(self):  # @TODO test with HALO_AWS
        header = {'HTTP_HOST': '127.0.0.2'}
        app.config['HALO_HOST'] = 'halo_app'
        app.config['SSM_TYPE'] = "XYZ"
        #app.config['PROVIDER'] = "AWS"
        #app.config['AWS_REGION'] = 'us-east-1'
        with app.test_request_context(method='GET', path='/?a=b', headers=header):
            try:
                from halo_app.ssm import set_app_param_config
                from halo_app.ssm import set_host_param_config
                params = {}
                params["url"] = set_host_param_config("halo_app:8000")
                set_app_param_config(app.config['SSM_TYPE'], params)
                import time
                print("sleep.")
                time.sleep(5.4)
                from halo_app.ssm import get_app_config
                config = get_app_config(app.config['SSM_TYPE'])
                eq_(config.get_param("halo_app")["url"], 'https://halo_flask:8000/loc')
            except Exception as e:
                eq_(e.__class__.__name__, "NotSSMTypeException")

    def test_43_ssm_onperm(self):  # @TODO
        header = {'HTTP_HOST': '127.0.0.2'}
        app.config['SSM_TYPE'] = "ONPREM"
        app.config['ONPREM_SSM_CLASS_NAME'] = 'OnPremClient'
        app.config['ONPREM_SSM_MODULE_NAME'] = 'halo_app.infra.providers.ssm.onprem_ssm_client'
        with app.test_request_context(method='GET', path='/?a=b', headers=header):
            from halo_app.ssm import set_app_param_config
            params = {}
            params["url"] = "124"
            set_app_param_config(app.config['SSM_TYPE'], params)
            from halo_app.ssm import get_app_config
            config = get_app_config(app.config['SSM_TYPE'])
            t = config.get_param('halo_app')
            print("t="+str(t))
            eq_(str(t), '<Section: halo_app>')#'<Section: DEFAULT>')



    def test_44_timeout(self):
        with app.test_request_context(method='GET', path='/?a=b'):
            os.environ["AWS_LAMBDA_FUNCTION_NAME"] = "halo_app"
            halo_context = client_util.get_halo_context(request.headers)
            timeout = Util.get_timeout(halo_context)
            eq_(timeout, 3)

    def test_45_CORR(self):
        headers = {'HTTP_HOST': '127.0.0.2','x-halo-correlation-id':"123"}
        app.config['HALO_CONTEXT_LIST'] = [HaloContext.CORRELATION]
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/',headers=headers):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z1", request.args)
            response = self.boundary.execute(halo_request)
            eq_(response.success,True)

    def test_46_NOCORR(self):
        header = {'HTTP_HOST': '127.0.0.2'}
        app.config['HALO_CONTEXT_LIST'] = [HaloContext.CORRELATION]
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/',headers=header):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z1", request.args)
            try:
                response = self.boundary.execute(halo_request)
                return False
            except Exception as e:
                eq_(e.__class__.__name__, "InternalServerError")

    def test_47_CORR(self):
        app.config['PROVIDER'] = "AWS"
        headers = {'HTTP_HOST': '127.0.0.2','x-tester-id':"123"}
        app.config['HALO_CONTEXT_LIST'] = [CAContext.TESTER]
        app.config['HALO_CONTEXT_CLASS'] = 'tests.test_halo.CAContext'
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/',headers=headers):
            halo_context = client_util.get_halo_context(request.headers)
            eq_(halo_context.get(CAContext.TESTER), "123")
            halo_request = SysUtil.create_command_request(halo_context, "z1", request.args)
            response = self.boundary.execute(halo_request)
            eq_(response.success,True)

    def test_48_NOCORR(self):
        header = {'HTTP_HOST': '127.0.0.2'}
        app.config['HALO_CONTEXT_LIST'] = [CAContext.TESTER]
        app.config['HALO_CONTEXT_CLASS'] = 'tests.test_halo.CAContext'
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/',headers=header):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z1", request.args)
            try:
                response = self.boundary.execute(halo_request)
                return False
            except Exception as e:
                eq_(e.__class__.__name__, "InternalServerError")

    def test_49_NOCORR(self):
        from halo_app.app.globals import load_global_data
        app.config["INIT_CLASS_NAME"] = 'halo_app.app.globals.GlobalService'
        app.config["INIT_DATA_MAP"] = {'INIT_STATE': "Idle", 'PROP_URL':
            "C:\\dev\\projects\\halo\\halo_app\\halo_app\\env\\config\\flask_setting_mapping.json"}
        load_global_data(app.config["INIT_CLASS_NAME"], app.config["INIT_DATA_MAP"])

    def test_50_db(self):
        app.config['DBACCESS_CLASS'] = 'tests.test_halo.DbMixin'
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/'):
            halo_context = client_util.get_halo_context(request.headers)
            db = DbTest()
            req = AbsHaloRequest(halo_context, "z1", {})
            db.get_dbaccess(req,True)

    def test_51_db(self):
        app.config['DBACCESS_CLASS'] = 'tests.test_halo.DbMixin'
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/'):
            halo_context = client_util.get_halo_context(request.headers)
            db = DbTest()
            req = AbsHaloRequest(halo_context, "z1", {})
            db.get_dbaccess(req,False)


    def test_52_security_need_token(self):
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/'):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z4", request.args)
            try:
                response = self.boundary.execute(halo_request)
                eq_(response.errors['error']["error_code"], 10108)
            except Exception as e:
                eq_(1, 2)

    def test_53_security_bad_token(self):
        app.config['SESSION_MINUTES'] = 30
        public_id = '12345'
        secret = '123456'#different token
        hdr = HaloSecurity.user_token(None, public_id,30,secret)
        headers = {'HTTP_HOST': '127.0.0.2', 'x-halo-access-token': hdr['token']}
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/',headers=headers):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z4", request.args)
            try:
                response = self.boundary.execute(halo_request)
                eq_(1,2)
            except Exception as e:
                eq_(e.data['errors']['error']["error_code"], 10109)

    def test_54_security_good_token(self):
        app.config['SESSION_MINUTES'] = 30
        secret = '123456'
        app.config['SECRET_KEY'] = secret
        public_id = '12345'
        hdr = HaloSecurity.user_token(None, public_id,30,secret)
        headers = {'HTTP_HOST': '127.0.0.2', 'x-halo-access-token': hdr['token']}
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/',headers=headers):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z1", request.args)
            try:
                response = self.boundary.execute(halo_request)
                eq_(1,2)
            except Exception as e:
                eq_(e.data['errors']['error']["error_code"], 500)

    def test_55_security_good_token_no_role_needed(self):
        app.config['SESSION_MINUTES'] = 30
        secret = '12345'
        app.config['SECRET_KEY'] = secret
        app.config['HALO_SECURITY_CLASS'] = 'tests.test_halo.Sec'
        public_id = '12345'
        hdr = HaloSecurity.user_token(None, public_id, 30, secret)
        headers = {'HTTP_HOST': '127.0.0.2', 'x-halo-access-token': hdr['token']}
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/', headers=headers):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z1", request.args)
            try:
                self.a4.method_roles = []
                response = self.boundary.execute(halo_request)
                eq_(1,2)
            except Exception as e:
                eq_(e.data['errors']['error']["error_code"], 500)

    def test_56_security_good_token_role_needed_missing(self):
        app.config['SESSION_MINUTES'] = 30
        secret = '12345'
        app.config['SECRET_KEY'] = secret
        app.config['HALO_SECURITY_CLASS'] = 'tests.test_halo.Sec'
        public_id = '12345'
        hdr = HaloSecurity.user_token(None, public_id, 30, secret)
        headers = {'HTTP_HOST': '127.0.0.2', 'x-halo-access-token': hdr['token']}
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/', headers=headers):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z1", request.args)
            try:
                self.a4.method_roles = ['tst1']
                response = self.boundary.execute(halo_request)
                eq_(1,2)
            except Exception as e:
                eq_(e.data['errors']['error']["error_code"], 500)

    def test_57_security_good_token_role_needed_exist(self):
        app.config['PROVIDER'] = "AWS"
        app.config['SESSION_MINUTES'] = 30
        secret = '12345'
        app.config['SECRET_KEY'] = secret
        app.config['HALO_SECURITY_CLASS'] = 'tests.test_halo.Sec'
        public_id = '12345'
        hdr = HaloSecurity.user_token(None, public_id, 30, secret)
        headers = {'HTTP_HOST': '127.0.0.2', 'x-halo-access-token': hdr['token']}
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/', headers=headers):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z1", request.args)
            try:
                self.a4.method_roles = ['tst']
                response = self.boundary.execute(halo_request)
                eq_(response.code,200)
            except Exception as e:
                print(str(e))
                eq_(1,2)

    def test_58_aws_invoke_sync_fail(self):
        app.config['PROVIDER'] = "AWS"
        app.config['SESSION_MINUTES'] = 30
        secret = '12345'
        app.config['SECRET_KEY'] = secret
        app.config['HALO_SECURITY_CLASS'] = 'tests.test_halo.Sec'
        public_id = '12345'
        hdr = HaloSecurity.user_token(None, public_id, 30, secret)
        headers = {'HTTP_HOST': '127.0.0.2', 'x-halo-access-token': hdr['token']}
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/', headers=headers):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z1", request.args)
            try:
                self.a5.method_roles = ['tst']
                response = self.boundary.execute(halo_request)
                eq_(1,2)
            except Exception as e:
                eq_(e.__class__, 'halo_aws.providers.cloud.aws.exceptions.ProviderException')

    def test_59_aws_invoke_sync_fail(self):
        app.config['PROVIDER'] = "AWS"
        app.config['SESSION_MINUTES'] = 30
        secret = '12345'
        app.config['SECRET_KEY'] = secret
        app.config['HALO_SECURITY_CLASS'] = 'tests.test_halo.Sec'
        public_id = '12345'
        hdr = HaloSecurity.user_token(None, public_id, 30, secret)
        headers = {'HTTP_HOST': '127.0.0.2', 'x-halo-access-token': hdr['token']}
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/', headers=headers):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z1", request.args)
            try:
                self.a6.method_roles = ['tst']
                response = self.boundary.execute(halo_request)
                eq_(1,2)
            except Exception as e:
                eq_(e.__class__, 'halo_aws.providers.cloud.aws.exceptions.ProviderException')

    def test_60_aws_invoke_sync_success(self):
        app.config['PROVIDER'] = "AWS"
        app.config['HALO_CONTEXT_LIST'] = ["CORRELATION"]
        app.config['SESSION_MINUTES'] = 30
        secret = '12345'
        app.config['SECRET_KEY'] = secret
        app.config['HALO_SECURITY_CLASS'] = 'tests.test_halo.Sec'
        public_id = '12345'
        hdr = HaloSecurity.user_token(None, public_id, 30, secret)
        headers = {'HTTP_HOST': '127.0.0.2', 'x-halo-access-token': hdr['token'],'x-halo-correlation-id':'123456'}
        with app.test_request_context(method='POST', path='/xst2/2/tst1/1/tst/0/', headers=headers):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z1", request.args)
            try:
                self.a5.method_roles = ['tst']
                response = self.boundary.execute(halo_request)
                eq_(response.code, 201)
            except Exception as e:
                print(str(e))
                eq_(1,2)

    def test_61_aws_invoke_sync_success(self):
        app.config['PROVIDER'] = "AWS"
        app.config['DEBUG'] = True
        app.config['HALO_CONTEXT_LIST'] = ["CORRELATION"]
        app.config['SESSION_MINUTES'] = 30
        secret = '12345'
        app.config['SECRET_KEY'] = secret
        app.config['HALO_SECURITY_CLASS'] = 'tests.test_halo.Sec'
        public_id = '12345'
        hdr = HaloSecurity.user_token(None, public_id, 30, secret)
        headers = {'HTTP_HOST': '127.0.0.2', 'x-halo-access-token': hdr['token'],'x-halo-correlation-id':'123456'}
        with app.test_request_context(method='POST', path='/xst2/2/tst1/1/tst/0/', headers=headers):
            halo_context = client_util.get_halo_context(request.headers)
            halo_request = SysUtil.create_command_request(halo_context, "z1", request.args)
            try:
                self.a6.method_roles = ['tst']
                response = self.boundary.execute(halo_request)
                eq_(response.code, 201)
            except Exception as e:
                print(str(e))
                eq_(1,2)

    def test_62_run_handle_with_entity_assembler(self):
        with app.test_request_context(method='GET', path='/?id=1'):
            try:
                halo_context = client_util.get_halo_context(request.headers)
                halo_request = SysUtil.create_command_request(halo_context, "z17", request.args)
                response = self.boundary.execute(halo_request)
                eq_(response.success,True)
                eq_(response.payload.data, "123")
            except Exception as e:
                print(str(e))
                eq_(e.__class__.__name__, "NoApiClassException")

    def test_63_run_handle_with_dto_assembler(self):
        with app.test_request_context(method='GET', path='/?id=2'):
            try:
                halo_context = client_util.get_halo_context(request.headers)
                halo_request = SysUtil.create_command_request(halo_context, "z17", request.args)
                response = self.boundary.execute(halo_request)
                eq_(response.success,True)
                eq_(response.payload.data, "456")
            except Exception as e:
                print(str(e))
                eq_(e.__class__.__name__, "NoApiClassException")

    def test_64_run_handle_with_dto_assembler(self):
        with app.test_request_context(method='GET', path='/?id=3'):
            try:
                halo_context = client_util.get_halo_context(request.headers)
                halo_request = SysUtil.create_command_request(halo_context, "z17", request.args)
                response = self.boundary.execute(halo_request)
                eq_(response.success,True)
                eq_(response.payload.data, "789")
            except Exception as e:
                print(str(e))
                eq_(e.__class__.__name__, "NoApiClassException")

    def test_65_run_handle_with_dto_assembler(self):
        with app.test_request_context(method='GET', path='/?id=4'):
            try:
                halo_context = client_util.get_halo_context(request.headers)
                halo_request = SysUtil.create_command_request(halo_context, "z17", request.args)
                response = self.boundary.execute(halo_request)
                eq_(response.success,True)
                eq_(response.payload.data, "789")
            except Exception as e:
                print(str(e))
                eq_(e.__class__.__name__, "NoApiClassException")

    def test_66_run_handle_with_dto_assembler_err(self):
        with app.test_request_context(method='GET', path='/?id=5'):
            try:
                halo_context = client_util.get_halo_context(request.headers)
                halo_request = SysUtil.create_command_request(halo_context, "z17", request.args)
                response = self.boundary.execute(halo_request)
                eq_(response.success,False)
                eq_(response.error.message, "msg")
            except Exception as e:
                print(str(e))
                eq_(e.__class__.__name__, "NoApiClassException")
