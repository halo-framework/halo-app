from __future__ import annotations

import json
import os
from dataclasses import dataclass

from halo_app.app.dto import AbsHaloDto
from halo_app.app.dto_assembler import DtoAssemblerFactory, AbsDtoAssembler
from halo_app.app.dto_mapper import AbsHaloDtoMapper
from halo_app.app.event import AbsHaloEvent
from halo_app.app.handlers import AbsCommandHandler, AbsEventHandler, AbsQueryHandler
from halo_app.app.notification import Notification
from halo_app.app.query import HaloQuery
from halo_app.app.request import AbsHaloRequest
from halo_app.app.request import HaloContext, HaloCommandRequest, HaloEventRequest, HaloQueryRequest
from halo_app.app.response import AbsHaloResponse, HaloResponseFactory, HaloCommandResponse
from halo_app.app.result import Result
from halo_app.app.uow import AbsUnitOfWork
from halo_app.const import HTTPChoice
from halo_app.domain.exceptions import AbsDomainException
from halo_app.domain.model import Item
from halo_app.domain.repository import AbsRepository
from halo_app.domain.service import AbsDomainService
from halo_app.entrypoints.client_type import ClientType
from halo_app.infra.apis import AbsRestApi, AbsSoapApi, SoapResponse, ApiMngr  # CnnApi,GoogleApi,TstApi
from halo_app.infra.exceptions import AbsInfraException
from halo_app.infra.mail import AbsMailService
from halo_app.infra.sql_repository import SqlAlchemyRepository
from halo_app.models import AbsDbMixin
from halo_app.security import HaloSecurity


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


class Sec(HaloSecurity):
    def get_secret(self):
        return '12345'
    def get_user_roles(self,user):
        return ['tst']

#API_LIST = {"Google": 'tests.test_halo.GoogleApi', "Cnn": "tests.test_halo.CnnApi","Tst":"tests.test_halo.TstApi","Tst2":"tests.test_halo.Tst2Api","Tst3":"tests.test_halo.Tst3Api","Tst4":"tests.test_halo.Tst4Api"}

#ApiMngr.set_api_list(API_LIST)

class ItemRepository(SqlAlchemyRepository):

    def __init__(self, session):
        super(ItemRepository, self).__init__(session)
        self.aggregate_type = Item


class A0(AbsCommandHandler):
    repository = None
    domain_service = None
    infra_service = None

    def __init__(self):
        super(A0,self).__init__()
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
            self.repository = uow(ItemRepository)
            item = None
            try:
                item = self.repository.get(halo_request.command.vars['id'])
            except Exception:
                pass
            if item is None:
                item = Item("1","test")
                self.repository.add(item)
            entity = self.domain_service.validate(item)
            self.infra_service.send(entity)
            uow.commit()
            payload = {"1": {"a": "b"}}
            return Result.ok(payload) #Util.create_response(halo_request, True, payload)

    def set_back_api(self,halo_request, foi=None):
        if not foi:#not in seq
            if halo_request.usecase_id == "z1" or halo_request.usecase_id == "z1a" or halo_request.usecase_id == "z5":
                return ApiMngr.get_api_instance("Cnn",halo_request.context,HTTPChoice.get.value)
                #return CnnApi(halo_request.context,HTTPChoice.delete.value)
        return None

    def extract_json(self,halo_request,api, back_response, seq=None):
        if seq == None:#no event
            if halo_request.usecase_id == "z1":
                return {"tst_get":"good"}
            if halo_request.usecase_id == "z1a":
                return {"tst_delete":"good"}
        else:#in event
            if halo_request.usecase_id == HTTPChoice.put.value:#method type
                if seq == '1':
                    return {"tst_put":"good1"}
                if seq == '2':
                    return {"tst_put":"good2"}
            if halo_request.usecase_id == HTTPChoice.post.value:#method type
                if seq == '1':
                    return {"tst_post":"good1"}
                if seq == '2':
                    return {"tst_post":"good2"}
            if halo_request.usecase_id == HTTPChoice.patch.value:#method type
                return {"tst_patch":"good"}
class A1(A0):
    pass

class A3(AbsCommandHandler):

    def do_filter(self, halo_request, halo_response):  #
        request_filter = self.get_request_filter(halo_request)
        request_filter.do_filter(halo_request, halo_response)

class A2(A1):

    def set_api_data(self,halo_request,api, seq=None, dict:dict=None):
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
            if halo_request.usecase_id == "z1":#method type
                return {"tst_get_deposit":"good"}
            else:
                return {"tst_delete_deposit":"good"}
        else:#in event
            if halo_request.usecase_id == "z1":#method type
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
        if halo_request.usecase_id == "z4" or halo_request.usecase_id == "z5" or halo_request.usecase_id == "z6":
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
        dto = ItemDto(entity.id,entity.data)
        return dto

    def write_entity(self,dto:ItemDto)->Item:
        entity = Item(dto.id,dto.data)
        return entity

    def write_dto_for_method(self, usecase_id: str,data,flag:str=None) -> AbsHaloDto:
        if usecase_id == "z17" and flag:
            return ItemDto(data["id"],data["data"])
        dto_mapper = DtoMapper()
        dto = dto_mapper.map_to_dto(data,ItemDto.__class__)
        return dto

class A17(A0):

    def handle(self,halo_request:HaloCommandRequest,uow:AbsUnitOfWork) ->Result:
        with uow:
            self.repository = uow(ItemRepository)
            if 'id' in halo_request.command.vars:
                if halo_request.command.vars['id'] == '1':
                    entity = Item("1","123")
                    self.repository.add(entity)
                    self.infra_service.send(entity)
                    uow.commit()
                    dto_assembler = DtoAssemblerFactory.get_assembler_by_entity(entity)
                    dto = dto_assembler.write_dto(entity)
                    payload = dto
                    return Result.ok(payload)
                if halo_request.command.vars['id'] == '2':
                    dto = ItemDto("2","456")
                    entity = Item("1", "123")
                    self.repository.add(entity)
                    uow.commit()
                    payload = dto
                    return Result.ok(payload)
                if halo_request.command.vars['id'] == '3':
                    dto_assembler = DtoAssemblerFactory.get_assembler_by_request(halo_request)
                    dto = dto_assembler.write_dto_for_method(halo_request.usecase_id, {"id": "1", "data": "789"}, "x")
                    uow.commit()
                    payload = dto
                    return Result.ok(payload)
                if halo_request.command.vars['id'] == '4':
                    dto_assembler = DtoAssemblerFactory.get_assembler_by_request(halo_request)
                    class d:
                        id = "1"
                        data = "789"
                    dto = dto_assembler.write_dto_for_method(halo_request.usecase_id, d())
                    uow.commit()
                    payload = dto
                    return Result.ok(payload)

                return Result.fail("code","msg","failx")

class TestHaloEvent(AbsHaloEvent):
    xid:str = None

    def __init__(self, mid, xid:str):
        super(TestHaloEvent, self).__init__(mid)
        self.xid = xid

class TestHaloQuery(HaloQuery):

    def __init__(self, name,vars):
        super(TestHaloQuery, self).__init__(name,vars)

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
