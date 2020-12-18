from __future__ import print_function

import json
import os

from faker import Faker
from flask import Flask, request
from nose.tools import eq_

from halo_app.app.mixinx import AbsCommandHandler, AbsQueryHandler
from halo_app.base_util import BaseUtil
from halo_app.circuitbreaker import CircuitBreakerError
from halo_app.data.finder import AbsFinder
from halo_app.domain.service import AbsDomainService
from halo_app.errors import status
from halo_app.exceptions import ApiError,HaloMethodNotImplementedException
from halo_app.domain.repository import AbsRepository
from halo_app.infra.service import AbsMailService
from halo_app.logs import log_json
from halo_app import saga
from halo_app.const import HTTPChoice, OPType
from halo_app.infra.apis import AbsRestApi, AbsSoapApi, SoapResponse, ApiMngr  # CnnApi,GoogleApi,TstApi
from halo_app.app.viewsx import BoundaryService
from halo_app.app.request import HaloContext, HaloCommandRequest, HaloQueryRequest
from halo_app.infra.apis import load_api_config
from halo_app.models import AbsDbMixin
from halo_app.ssm import set_app_param_config,get_app_param_config,set_host_param_config
from halo_app.app.viewsx import load_global_data
from halo_app.security import HaloSecurity
from halo_app.app.utilx import Util
import unittest

#6,7,9923,9941 failing
from halo_app.sys_util import SysUtil

fake = Faker()
app = Flask(__name__)

from halo_app.app.request import HaloRequest

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
from halo_app.circuitbreaker import CircuitBreaker,CircuitBreakerMonitor
from requests.exceptions import RequestException
class MyCircuitBreaker(CircuitBreaker):
    FAILURE_THRESHOLD = 3
    RECOVERY_TIMEOUT = 60
    EXPECTED_EXCEPTION = RequestException

class CnnApi(AbsRestApi):
    name = 'Cnn'

    @MyCircuitBreaker()
    def do_cb_request(self, method, url, timeout, data=None, headers=None, auth=None):
        return super(CnnApi,self).do_cb_request(method, url, timeout, data=None, headers=None, auth=None)

class GoogleApi(AbsRestApi):
    name = 'Google'

class TstApi(AbsRestApi):
    name = 'Tst'

    @MyCircuitBreaker()
    def do_cb_request(self, method, url, timeout, data=None, headers=None, auth=None):
        return super(TstApi, self).do_cb_request(method, url, timeout, data=None, headers=None, auth=None)

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

#API_LIST = {"Google": 'tests.test_flask.GoogleApi', "Cnn": "tests.test_flask.CnnApi","Tst":"tests.test_flask.TstApi","Tst2":"tests.test_flask.Tst2Api","Tst3":"tests.test_flask.Tst3Api","Tst4":"tests.test_flask.Tst4Api"}

#ApiMngr.set_api_list(API_LIST)

class A1(BoundaryService,AbsCommandHandler):
    repository = None
    domain_service = None
    infra_service = None

    def __init__(self):
        super(A1,self).__init__()
        self.repository = AbsRepository()
        self.domain_service = AbsDomainService()
        self.infra_service = AbsMailService()

    def handle(self,halo_command_request:HaloCommandRequest) ->dict:
        item = self.repository.load(halo_command_request.vars['id'])
        entity = self.domain_service.validate(item)
        self.infra_service.send(entity)
        return {"1":{"a":"b"}}

    def set_back_api(self,halo_request, foi=None):
        if not foi:#not in seq
            if halo_request.method_id == "z1" or halo_request.method_id == "z3":
                return ApiMngr.get_api_instance("Cnn",halo_request.context,HTTPChoice.delete.value)
                #return CnnApi(halo_request.context,HTTPChoice.delete.value)
        return super(A1,self).set_back_api(halo_request,foi)

    def extract_json(self,halo_request,api, back_response, seq=None):
        if seq == None:#no event
            if halo_request.method_id == HTTPChoice.get.value:#method type
                return {"tst_get":"good"}
            if halo_request.method_id == HTTPChoice.delete.value:#method type
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

class A3(BoundaryService,AbsCommandHandler):

    def do_operation(self, halo_request):
        # 1. validate input params
        self.validate_req(halo_request)
        # 2. run pre conditions
        self.validate_pre(halo_request)
        # 3. processing engine abc
        # 4. Build the payload target response structure which is Compliant
        payload = self.create_resp_payload(halo_request, {})
        # 5. setup headers for reply
        headers = self.set_resp_headers(halo_request)
        # 6. build json and add to halo response
        halo_response = self.create_response(halo_request, payload, headers)
        # 7. post condition
        self.validate_post(halo_request, halo_response)
        # 8. do filter
        self.do_filter(halo_request,halo_response)
        # 9. return json response
        return halo_response

    def do_filter(self, halo_request, halo_response):  #
        request_filter = self.get_request_filter(halo_request)
        request_filter.do_filter(halo_request, halo_response)

class A2(A1):

    def set_api_data(self,halo_request,api, seq=None, dict=None):
        if halo_request.context.get(HaloContext.method) == HTTPChoice.post.value:
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
            if halo_request.context.get(HaloContext.method) == HTTPChoice.delete.value:#method type
                return {"tst_delete_deposit":"good"}
        else:#in event
            if halo_request.context.get(HaloContext.method) == HTTPChoice.put.value:#method type
                if seq == '1':
                    return {"tst_put_deposit":"good1"}
                if seq == '2':
                    return {"tst_put_deposit":"good2"}
            if halo_request.context.get(HaloContext.method) == HTTPChoice.post.value:#method type
                if seq == '1':
                    return {"tst_post_deposit":"good1"}
                if seq == '2':
                    return {"tst_post_deposit":"good2"}
            if halo_request.context.get(HaloContext.method) == HTTPChoice.patch.value:#method type
                return {"tst_patch_deposit":"good"}

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

class A4(A2):
    secure = True

class A5(BoundaryService,AbsCommandHandler):
    secure = True

class A6(A5):
    pass


class A7(BoundaryService,AbsQueryHandler):
    finder = None

    def __init__(self):
        super(A7, self).__init__()
        self.finder = AbsFinder()

    def run(self, halo_query_request: HaloQueryRequest) -> dict:
        items = self.finder.find(halo_query_request.vars)
        return {"1": {"a": "c"}}



from halo_app.app.filterx import RequestFilter,RequestFilterClear
class TestFilter(RequestFilter):
    def augment_event_with_headers_and_data(self,event, halo_request,halo_response):
        event.put(HaloContext.items.get(HaloContext.CORRELATION), halo_request.context.get(HaloContext.items.get(HaloContext.CORRELATION)))
        return event

class TestRequestFilterClear(RequestFilterClear):
    def run(self,event):
        print("insert_events_to_repository " + str(event.serialize()))

class TestAwsRequestFilterClear(RequestFilterClear):
    def run(self,event):
        from halo_app.providers.providers import get_provider
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

def get_halo_context(request):
    context = Util.get_halo_context()
    for i in request.headers.keys():
        if type(i) == str:
            context.put(i,request.headers[i])
    context.put(HaloContext.method,request.method)
    return context

class TestUserDetailTestCase(unittest.TestCase):
    """
    Tests /users detail operations.
    """
    def start(self):
        from halo_app.const import LOC
        app.config['ENV_TYPE'] = LOC
        app.config['SSM_TYPE'] = "AWS"
        app.config['PROVIDER'] = "AWS"
        app.config['FUNC_NAME'] = "FUNC_NAME"
        #app.config['API_CONFIG'] = None
        app.config['AWS_REGION'] = 'us-east-1'
        #app.config['CIRCUIT_BREAKER'] = False
        with app.test_request_context(method='GET', path='/?abc=def'):
            try:
                load_api_config(app.config['ENV_TYPE'], app.config['SSM_TYPE'], app.config['FUNC_NAME'],
                                app.config['API_CONFIG'])
            except Exception as e:
                eq_(e.__class__.__name__, "NoApiClassException")

    def setUp(self):
        #self.url = 'http://127.0.0.1:8000/?abc=def'
        #self.perf_url = 'http://127.0.0.1:8000/perf'
        #app.config['TESTING'] = True
        #app.config['WTF_CSRF_ENABLED'] = False
        #app.config['DEBUG'] = False
        #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' +  os.path.join(app.config['BASEDIR'], TEST_DB)
        #self.app = app#.test_client()
        #app.config.from_pyfile('../settings.py')
        app.config.from_object('settings')
        self.a1 = A1()
        self.a2 = A2()
        self.a3 = A3()
        self.a4 = A4()
        self.a5 = A5()
        self.a6 = A6()
        self.a7 = A7()

        #self.start()

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

    def test_1_get_request_returns_exception(self):
        with app.test_request_context(method='GET', path='/?abc=def'):
            try:
                halo_context = get_halo_context(request)
                halo_request = SysUtil.create_request(halo_context, "z0", {'id':'1'})
                response = self.a1.process(halo_request)
                eq_(response.payload,{'a': 'b'})
            except Exception as e:
                print(str(e))
                eq_(e.__class__.__name__, "NoApiClassException")

    def test_2_delete_request_returns_dict(self):
        with app.test_request_context(method='DELETE', path='/?abc=def'):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z2", {})
            response = self.a1.process(halo_request)
            eq_(response.payload, {'1': None, '2': None, '3': None})

    def test_3_put_request_returns_dict(self):
        with app.test_request_context(method='PUT', path='/?abc=def'):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z3", {})
            response = self.a1.process(halo_request)
            eq_(response.payload, {'1': None, '2': None, '3': None})

    def test_4_cli(self):
        halo_context = HaloContext()
        halo_request = SysUtil.create_request(halo_context, "z3", {})
        response = self.a1.process(halo_request)
        eq_(response.payload, {'1': None, '2': None, '3': None})

    def test_41_cli_command(self):
        halo_context = HaloContext()
        halo_request = SysUtil.create_request(halo_context, "z3", {})
        response = self.a1.execute(halo_request)
        eq_(response.payload, {'1': None, '2': None, '3': None})

    def test_42_cli_query(self):
        halo_context = HaloContext()
        halo_request = SysUtil.create_request(halo_context, "z3", {},OPType.query)
        response = self.a7.execute(halo_request)
        eq_(response.payload, {'a': 'c'})

    def test_5_query_request_returns_dict(self):
        with app.test_request_context(method='GET', path='/?id=1'):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z3", request.args,OPType.query)
            response = self.a7.execute(halo_request)
            eq_(response.payload, {'a': 'c'})


    def test_6_api_request_returns_a_CircuitBreakerError(self):
        app.config['PROVIDER'] = "AWS"
        app.config['CIRCUIT_BREAKER'] = True
        with app.test_request_context(method='GET', path='/?a=b'):
            halo_context = get_halo_context(request)
            api = TstApi(halo_context)
            from halo_app.app.utilx import Util
            timeout = Util.get_timeout(halo_context)
            try:
                response = api.get(timeout)
            except ApiError as e:
                pass
            try:
                response = api.get(timeout)
            except ApiError as e:
                pass
            try:
                response = api.get(timeout)
            except ApiError as e:
                pass
            try:
                response = api.get(timeout)
            except ApiError as e:
                print(str(e))
                eq_(e.__class__.__name__, "ApiError")

    def test_7_api_request_returns_success(self):
        app.config['PROVIDER'] = "AWS"
        app.config['CIRCUIT_BREAKER'] = True
        #self.test_6_api_request_returns_a_CircuitBreakerError()
        with app.test_request_context(method='GET', path='/?a=b'):
            halo_context = get_halo_context(request)
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
            for c in CircuitBreakerMonitor.get_open():
                print(str(c))
            api = CnnApi(halo_context)
            timeout = Util.get_timeout(halo_context)
            try:
                response = api.get(timeout)
                for c in CircuitBreakerMonitor.get_circuits():
                    print(str(c))
                eq_(response.status_code, status.HTTP_200_OK)
            except ApiError as e:
                eq_(1,2)

    def test_80_api_request_returns_a_fail(self):
        with app.test_request_context(method='GET', path='/?a=b'):
            halo_context = get_halo_context(request)
            api = CnnApi(halo_context)
            api.url = api.url + "/lgkmlgkhm??l,mhb&&,g,hj "
            timeout = Util.get_timeout(halo_context)
            try:
                response = api.get(timeout)
                assert False
            except ApiError as e:
                eq_(e.status_code, status.HTTP_404_NOT_FOUND)
                #eq_(e.__class__.__name__,"CircuitBreakerError")

    def test_810_api_request_soap_returns(self):
        with app.test_request_context(method='GET', path='/'):
            halo_context = get_halo_context(request)
            api = Tst2Api(halo_context,method='method1')
            timeout = Util.get_timeout(halo_context)
            try:
                data = {}
                data['first'] = 'start'
                data['second'] = 'end'
                response = api.run(timeout,data)
                print("response=" + str(response.content))
                eq_(json.loads(response.content)['msg'],'Your input parameters are start and end')
            except ApiError as e:
                #eq_(e.status_code, status.HTTP_404_NOT_FOUND)
                eq_(response.payload['first'],'start')

    def test_811_api_request_soap_returns(self):
        app.config['CIRCUIT_BREAKER'] = True
        with app.test_request_context(method='GET', path='/'):
            halo_context = get_halo_context(request)
            api = Tst2Api(halo_context,method='method1')
            timeout = Util.get_timeout(halo_context)
            try:
                data = {}
                data['first'] = 'start'
                data['second'] = 'end'
                response = api.run(timeout,data)
                print("response=" + str(response.content))
                eq_(json.loads(response.content)['msg'],'Your input parameters are start and end')
            except ApiError as e:
                #eq_(e.status_code, status.HTTP_404_NOT_FOUND)
                eq_(response.payload['first'],'start')

    def test_812_api_request_soap_returns(self):
        app.config['CIRCUIT_BREAKER'] = True
        with app.test_request_context(method='GET', path='/'):
            halo_context = get_halo_context(request)
            api = Tst2Api(halo_context,method='method2')
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

    def test_82_api_request_rpc_returns(self):
        app.config['PROVIDER'] = "AWS"
        with app.test_request_context(method='GET', path='/?a=b'):
            halo_context = get_halo_context(request)
            api = Tst3Api(halo_context)
            timeout = Util.get_timeout(halo_context)
            try:
                response = api.get(timeout)
                assert False
            except ApiError as e:
                #eq_(e.status_code, status.HTTP_404_NOT_FOUND)
                eq_(e.__class__.__name__,"ApiError")

    def test_83_api_request_event_returns(self):
        app.config['PROVIDER'] = "AWS"
        with app.test_request_context(method='GET', path='/?a=b'):
            halo_context = get_halo_context(request)
            api = Tst4Api(halo_context)
            timeout = Util.get_timeout(halo_context)
            try:
                response = api.get(timeout)
                assert False
            except ApiError as e:
                eq_(e.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
                #eq_(e.__class__.__name__,"CircuitBreakerError")

    def test_9_send_event(self):
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

    def test_900_event_filter(self):
        app.config['SSM_TYPE'] = "AWS"
        app.config['AWS_REGION'] = 'us-east-1'
        app.config['PROVIDER'] = "AWS"
        app.config['REQUEST_FILTER_CLASS'] = 'test_flask.TestFilter'
        with app.test_request_context(method='POST', path='/?id=b',headers= {HaloContext.items.get(HaloContext.CORRELATION):"123"},data={"a":"1"}):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            response = self.a2.process(halo_request)
            eq_(response.payload, [{'id': 1, 'name': 'Pankaj', 'salary': '10000'}, {'name': 'David', 'salary': '5000', 'id': 2}])

    def test_901_event_filter(self):
        app.config['PROVIDER'] = "AWS"
        app.config['REQUEST_FILTER_CLASS'] = 'test_flask.TestFilter'
        with app.test_request_context(method='GET', path='/?id=b',headers= {HaloContext.items.get(HaloContext.CORRELATION):"123"}):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            response = self.a2.process(halo_request)
            eq_(response.payload, [{'id': 1, 'name': 'Pankaj', 'salary': '10000'}, {'name': 'David', 'salary': '5000', 'id': 2}])

    def test_902_event_filter(self):
        app.config['PROVIDER'] = "AWS"
        app.config['REQUEST_FILTER_CLASS'] = 'test_flask.TestFilter'
        app.config['REQUEST_FILTER_CLEAR_CLASS'] = 'test_flask.TestRequestFilterClear'
        with app.test_request_context(method='GET', path='/?id=b',headers= {HaloContext.items.get(HaloContext.CORRELATION):"123"}):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            response = self.a2.process(halo_request)

    def test_903_event_filter(self):
        app.config['PROVIDER'] = "AWS"
        app.config['REQUEST_FILTER_CLASS'] = 'test_flask.TestFilter'
        app.config['REQUEST_FILTER_CLEAR_CLASS'] = 'test_flask.TestRequestFilterClear'
        with app.test_request_context(method='GET', path='/?id=b',headers= {HaloContext.items.get(HaloContext.CORRELATION):"123"}):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            response = self.a2.execute(halo_request)

    def test_904_event_filter(self):
        app.config['PROVIDER'] = "AWS"
        app.config['REQUEST_FILTER_CLASS'] = 'test_flask.TestFilter'
        app.config['REQUEST_FILTER_CLEAR_CLASS'] = 'test_flask.TestAwsRequestFilterClear'
        with app.test_request_context(method='GET', path='/?id=b',headers= {HaloContext.items.get(HaloContext.CORRELATION):"123"}):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z10", request.args)
            response = self.a2.execute(halo_request)

    def test_905_filter(self):
        app.config['PROVIDER'] = "AWS"
        app.config['REQUEST_FILTER_CLASS'] = 'test_flask.TestFilter'
        app.config['REQUEST_FILTER_CLEAR_CLASS'] = 'test_flask.TestAwsRequestFilterClear'
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
                from halo_app.data.filters import Filter
                arr = []
                for f in filters:
                    filter = Filter(f.field, f.OP, f.value)
                    arr.append(filter)

            except Exception as e:
                raise e

    def test_906_filter(self):
        app.config['PROVIDER'] = "AWS"
        app.config['REQUEST_FILTER_CLASS'] = 'test_flask.TestFilter'
        app.config['REQUEST_FILTER_CLEAR_CLASS'] = 'test_flask.TestAwsRequestFilterClear'
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
                from halo_app.data.filters import Filter
                arr = []
                for f in filters:
                    filter = Filter(f.field, f.OP, f.value)
                    arr.append(filter)

            except Exception as e:
                eq_(e.__class__.__name__, "ValidationError")

    def test_907_filter(self):
        app.config['PROVIDER'] = "AWS"
        app.config['REQUEST_FILTER_CLASS'] = 'test_flask.TestFilter'
        app.config['REQUEST_FILTER_CLEAR_CLASS'] = 'test_flask.TestAwsRequestFilterClear'
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
                from halo_app.data.filters import Filter
                arr = []
                for f in filters:
                    filter = Filter(f.field, f.OP, f.value)
                    arr.append(filter)
                for f in arr:
                    if f.field == "weight":
                        eq_(True,f.apply(11))

            except Exception as e:
                eq_(e.__class__.__name__, "ValidationError")

    def test_908_filter(self):
        app.config['PROVIDER'] = "AWS"
        app.config['REQUEST_FILTER_CLASS'] = 'test_flask.TestFilter'
        app.config['REQUEST_FILTER_CLEAR_CLASS'] = 'test_flask.TestAwsRequestFilterClear'
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
                from halo_app.data.filters import Filter
                arr = []
                for f in filters:
                    filter = Filter(f.field, f.OP, f.value)
                    arr.append(filter)
                for f in arr:
                    if f.field == "weight":
                        eq_(False,f.apply(10))

            except Exception as e:
                eq_(e.__class__.__name__, "ValidationError")

    def test_91_system_debug_enabled(self):
        with app.test_request_context(method='GET', path='/?a=b'):
            os.environ['DEBUG_LOG'] = 'true'
            flag = 'false'
            for i in range(0, 180):
                ret = Util.get_system_debug_enabled()
                print(ret)
                if ret == 'true':
                    flag = ret
            eq_(flag, 'true')

    def test_92_debug_enabled(self):
        app.config['PROVIDER'] = "AWS"
        #headers = {'HTTP_X_HALO_DEBUG_LOG_ENABLED': 'true'}
        headers = {'x-halo-debug-log-enabled': 'true'}
        with app.test_request_context(method='GET', path='/?a=b', headers=headers):
            ret = get_halo_context(request)
            print(HaloContext.items[HaloContext.DEBUG_LOG])
            print(ret.table)
            eq_(ret.table["Http-"+HaloContext.items[HaloContext.DEBUG_LOG]], 'true')

    def test_93_json_log(self):
        import traceback
        app.config['PROVIDER'] = "AWS"
        #headers = {'HTTP_X_HALO_DEBUG_LOG_ENABLED': 'true'}
        headers = {'x-halo-debug-log-enabled': 'true'}
        with app.test_request_context(method='GET', path='/?a=b', headers=headers):
            halo_context = get_halo_context(request)
            try:
                raise Exception("test it")
            except Exception as e:
                e.stack = traceback.format_exc()
                ret = log_json(halo_context, {"abc": "def"}, err=e)
                print(str(ret))
                eq_(ret[HaloContext.items[HaloContext.DEBUG_LOG]], 'true')

    def test_94_get_request_with_debug(self):
        app.config['PROVIDER'] = 'ONPREM'
        headers = {'x-halo-debug-log-enabled': 'true'}
        with app.test_request_context(method='GET', path='/?a=b', headers=headers):
            halo_context = get_halo_context(request)
            ret = Util.get_debug_enable(halo_context)
            eq_(ret, 'true')

    def test_95_debug_event(self):
        event = {HaloContext.items[HaloContext.DEBUG_LOG]: 'true'}
        ret = BaseUtil.get_correlation_from_event(event)
        eq_(BaseUtil.event_req_context[HaloContext.items[HaloContext.DEBUG_LOG]], 'true')
        ret = BaseUtil.get_correlation_from_event(event)
        eq_(ret[HaloContext.items[HaloContext.DEBUG_LOG]], 'true')



    def test_98_run_simple_delete(self):
        with app.test_request_context(method='DELETE', path="/start?id=a"):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            response = self.a2.execute(halo_request)
            eq_(response.code, status.HTTP_200_OK)

    def test_990_run_seq_get(self):
        with app.test_request_context(method='GET', path="/?id=a"):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            response = self.a2.execute(halo_request)
            eq_(response.code, status.HTTP_200_OK)

    def test_991_load_saga(self):
        with app.test_request_context(method='POST', path="/"):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            with open("../env/config/saga.json") as f:
                jsonx = json.load(f)
            sagax = saga.load_saga("test",halo_request, jsonx, app.config['SAGA_SCHEMA'])
            eq_(len(sagax.actions), 6)

    def test_9920_run_saga(self):
        with app.test_request_context(method='POST', path="/?id=a"):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            response = self.a2.execute(halo_request)
            eq_(response.code, status.HTTP_201_CREATED)

    def test_9921_run_saga_bq(self):
        with app.test_request_context(method='POST', path="/tst?id=deposit"):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z3", request.args)
            response = self.a2.execute(halo_request)
            eq_(response.code, status.HTTP_201_CREATED)

    def test_9922_run_saga_bq_error(self):
        with app.test_request_context(method='POST', path="/tst?sub_func=tst"):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z4", request.args)
            try:
                response = self.a2.execute(halo_request)
                eq_(1,2)
            except Exception as e:
                eq_(e.__class__.__name__, "InternalServerError")

    def test_9923_trans_json(self):
        with app.test_request_context(method='GET', path="/tst"):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            try:
                response = self.a2.execute(halo_request)
                eq_(response.payload, [{"id": 1, "name": "Pankaj", "salary": "10000"}, {"name": "David", "salary": "5000", "id": 2}])
            except Exception as e:
                eq_(e.__class__.__name__, "InternalServerError")

    def test_9930_rollback_saga(self):
        with app.test_request_context(method='PUT', path="/"):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            try:
                response = self.a2.execute(halo_request)
                assert False
            except Exception as e:
                eq_(e.__class__.__name__, "ApiError")

    def test_9931_rollback_saga_error(self):
        with app.test_request_context(method='PATCH', path="/"):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            try:
                response = self.a2.execute(halo_request)
                assert False
            except Exception as e:
                eq_(e.__class__.__name__, "SagaError")


    def test_9932_all_rollback_saga(self):
        with app.test_request_context(method='PUT', path="/"):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            try:
                response = self.a2.execute(halo_request)
                assert False
            except Exception as e:
                eq_(e.__class__.__name__, "InternalServerError")

    def test_9933_all_rollback_saga_bq(self):
        with app.test_request_context(method='PUT', path="/test?sub_func=deposit"):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            try:
                response = self.a2.execute(halo_request)
                assert False
            except Exception as e:
                eq_(e.__class__.__name__, "InternalServerError")

    def test_9940_ssm_aws(self):  # @TODO test without HALO_AWS
        header = {'HTTP_HOST': '127.0.0.2'}
        app.config['HALO_HOST'] = 'halo_app'
        app.config['SSM_TYPE'] = "AWS"
        #app.config['PROVIDER'] = "AWS"
        app.config['AWS_REGION'] = 'us-east-1'
        with app.test_request_context(method='GET', path='/?a=b', headers=header):
            halo_context = get_halo_context(request)
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
                eq_(e.__class__.__name__, "ProviderError")

    def test_9941_ssm_aws(self):  # @TODO test with HALO_AWS
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

    def test_9942_ssm_aws(self):  # @TODO test with HALO_AWS
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

    def test_9944_ssm_aws(self):  # @TODO test with HALO_AWS
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
                eq_(e.__class__.__name__, "NoSSMDefinedError")

    def test_9945_ssm_aws(self):  # @TODO test with HALO_AWS
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
                eq_(e.__class__.__name__, "NotSSMTypeError")

    def test_995_ssm_onperm(self):  # @TODO
        header = {'HTTP_HOST': '127.0.0.2'}
        app.config['SSM_TYPE'] = "ONPREM"
        app.config['ONPREM_SSM_CLASS_NAME'] = 'OnPremClient'
        app.config['ONPREM_SSM_MODULE_NAME'] = 'halo_app.providers.ssm.onprem_ssm_client'
        with app.test_request_context(method='GET', path='/?a=b', headers=header):
            from halo_app.ssm import set_app_param_config
            params = {}
            params["url"] = "124"
            set_app_param_config(app.config['SSM_TYPE'], params)
            from halo_app.ssm import get_app_config
            config = get_app_config(app.config['SSM_TYPE'])
            t = config.get_param('halo_app')
            print("t="+str(t))
            eq_(str(t), '<Section: FUNC_NAME>')#'<Section: DEFAULT>')



    def test_997_timeout(self):
        with app.test_request_context(method='GET', path='/?a=b'):
            os.environ["AWS_LAMBDA_FUNCTION_NAME"] = "halo_app"
            halo_context = get_halo_context(request)
            timeout = Util.get_timeout(halo_context)
            eq_(timeout, 3)




    def test_9991_tst2_get(self):
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/'):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            response = self.a2.execute(halo_request)
            eq_(response.code, status.HTTP_200_OK)

    def test_99911_filter(self):
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/'):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            response = self.a3.do_process(halo_request)
            eq_(response.code, status.HTTP_200_OK)

    def test_99911_filter(self):
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/'):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            response = self.a3.do_process(halo_request)
            eq_(response.code, status.HTTP_200_OK)

    def test_9992_CORR(self):
        headers = {'HTTP_HOST': '127.0.0.2','x-correlation-id':"123"}
        app.config['HALO_CONTEXT_LIST'] = [HaloContext.CORRELATION]
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/',headers=headers):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            response = self.a2.execute(halo_request)
            eq_(response.code, status.HTTP_200_OK)

    def test_9993_NOCORR(self):
        header = {'HTTP_HOST': '127.0.0.2'}
        app.config['HALO_CONTEXT_LIST'] = [HaloContext.CORRELATION]
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/',headers=header):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            try:
                response = self.a2.execute(halo_request)
                return False
            except Exception as e:
                eq_(e.__class__.__name__, "InternalServerError")

    def test_9994_CORR(self):
        app.config['PROVIDER'] = "AWS"
        headers = {'HTTP_HOST': '127.0.0.2','x-tester-id':"123"}
        app.config['HALO_CONTEXT_LIST'] = [CAContext.TESTER]
        app.config['HALO_CONTEXT_CLASS'] = 'test_flask.CAContext'
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/',headers=headers):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            response = self.a2.execute(halo_request)
            eq_(response.status_code, status.HTTP_200_OK)

    def test_9995_NOCORR(self):
        header = {'HTTP_HOST': '127.0.0.2'}
        app.config['HALO_CONTEXT_LIST'] = [CAContext.TESTER]
        app.config['HALO_CONTEXT_CLASS'] = 'test_flask.CAContext'
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/',headers=header):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            try:
                response = self.a2.execute(halo_request)
                return False
            except Exception as e:
                eq_(e.__class__.__name__, "InternalServerError")

    def test_9996_NOCORR(self):
        from halo_app.app.viewsx import load_global_data
        app.config["INIT_CLASS_NAME"] = 'halo_app.app.viewsx.GlobalService'
        app.config["INIT_DATA_MAP"] = {'INIT_STATE': "Idle", 'PROP_URL':
            "C:\\dev\\projects\\halo\\halo_app\\halo_app\\env\\config\\flask_setting_mapping.json"}
        load_global_data(app.config["INIT_CLASS_NAME"], app.config["INIT_DATA_MAP"])

    def test_9997_db(self):
        app.config['DBACCESS_CLASS'] = 'test_flask.DbMixin'
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/'):
            halo_context = get_halo_context(request)
            db = DbTest()
            req = HaloRequest(halo_context,"z1",{})
            db.get_dbaccess(req,True)

    def test_9998_db(self):
        app.config['DBACCESS_CLASS'] = 'test_flask.DbMixin'
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/'):
            halo_context = get_halo_context(request)
            db = DbTest()
            req = HaloRequest(halo_context,"z1",{})
            db.get_dbaccess(req,False)


    def test_99991_security_need_token(self):
        app.config['CIRCUIT_BREAKER'] = False
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/'):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            try:
                response = self.a4.execute(halo_request)
                eq_(1,2)
            except Exception as e:
                eq_(e.data['errors']['error']["error_code"], 10108)

    def test_99992_security_bad_token(self):
        app.config['CIRCUIT_BREAKER'] = False
        app.config['SESSION_MINUTES'] = 30
        public_id = '12345'
        secret = '123456'#different token
        hdr = HaloSecurity.user_token(None, public_id,30,secret)
        headers = {'HTTP_HOST': '127.0.0.2', 'x-halo-access-token': hdr['token']}
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/',headers=headers):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            try:
                response = self.a4.execute(halo_request)
                eq_(1,2)
            except Exception as e:
                eq_(e.data['errors']['error']["error_code"], 10109)

    def test_99992_security_good_token(self):
        app.config['CIRCUIT_BREAKER'] = False
        app.config['SESSION_MINUTES'] = 30
        secret = '123456'
        app.config['SECRET_KEY'] = secret
        public_id = '12345'
        hdr = HaloSecurity.user_token(None, public_id,30,secret)
        headers = {'HTTP_HOST': '127.0.0.2', 'x-halo-access-token': hdr['token']}
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/',headers=headers):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            try:
                response = self.a4.execute(halo_request)
                eq_(1,2)
            except Exception as e:
                eq_(e.data['errors']['error']["error_code"], 500)

    def test_99993_security_good_token_no_role_needed(self):
        app.config['CIRCUIT_BREAKER'] = False
        app.config['SESSION_MINUTES'] = 30
        secret = '12345'
        app.config['SECRET_KEY'] = secret
        app.config['HALO_SECURITY_CLASS'] = 'tests.test_flask.Sec'
        public_id = '12345'
        hdr = HaloSecurity.user_token(None, public_id, 30, secret)
        headers = {'HTTP_HOST': '127.0.0.2', 'x-halo-access-token': hdr['token']}
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/', headers=headers):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            try:
                self.a4.method_roles = []
                response = self.a4.execute(halo_request)
                eq_(1,2)
            except Exception as e:
                eq_(e.data['errors']['error']["error_code"], 500)

    def test_99994_security_good_token_role_needed_missing(self):
        app.config['CIRCUIT_BREAKER'] = False
        app.config['SESSION_MINUTES'] = 30
        secret = '12345'
        app.config['SECRET_KEY'] = secret
        app.config['HALO_SECURITY_CLASS'] = 'tests.test_flask.Sec'
        public_id = '12345'
        hdr = HaloSecurity.user_token(None, public_id, 30, secret)
        headers = {'HTTP_HOST': '127.0.0.2', 'x-halo-access-token': hdr['token']}
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/', headers=headers):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            try:
                self.a4.method_roles = ['tst1']
                response = self.a4.execute(halo_request)
                eq_(1,2)
            except Exception as e:
                eq_(e.data['errors']['error']["error_code"], 500)

    def test_99995_security_good_token_role_needed_exist(self):
        app.config['PROVIDER'] = "AWS"
        app.config['CIRCUIT_BREAKER'] = False
        app.config['SESSION_MINUTES'] = 30
        secret = '12345'
        app.config['SECRET_KEY'] = secret
        app.config['HALO_SECURITY_CLASS'] = 'tests.test_flask.Sec'
        public_id = '12345'
        hdr = HaloSecurity.user_token(None, public_id, 30, secret)
        headers = {'HTTP_HOST': '127.0.0.2', 'x-halo-access-token': hdr['token']}
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/', headers=headers):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            try:
                self.a4.method_roles = ['tst']
                response = self.a4.execute(halo_request)
                eq_(response.code,200)
            except Exception as e:
                print(str(e))
                eq_(1,2)

    def test_99996_aws_invoke_sync_fail(self):
        app.config['PROVIDER'] = "AWS"
        app.config['CIRCUIT_BREAKER'] = False
        app.config['SESSION_MINUTES'] = 30
        secret = '12345'
        app.config['SECRET_KEY'] = secret
        app.config['HALO_SECURITY_CLASS'] = 'tests.test_flask.Sec'
        public_id = '12345'
        hdr = HaloSecurity.user_token(None, public_id, 30, secret)
        headers = {'HTTP_HOST': '127.0.0.2', 'x-halo-access-token': hdr['token']}
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/', headers=headers):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            try:
                self.a5.method_roles = ['tst']
                response = self.a5.process(halo_request)
                eq_(1,2)
            except Exception as e:
                eq_(e.__class__, 'halo_aws.providers.cloud.aws.exceptions.ProviderError')

    def test_99997_aws_invoke_sync_fail(self):
        app.config['PROVIDER'] = "AWS"
        app.config['CIRCUIT_BREAKER'] = False
        app.config['SESSION_MINUTES'] = 30
        secret = '12345'
        app.config['SECRET_KEY'] = secret
        app.config['HALO_SECURITY_CLASS'] = 'tests.test_flask.Sec'
        public_id = '12345'
        hdr = HaloSecurity.user_token(None, public_id, 30, secret)
        headers = {'HTTP_HOST': '127.0.0.2', 'x-halo-access-token': hdr['token']}
        with app.test_request_context(method='GET', path='/xst2/2/tst1/1/tst/0/', headers=headers):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            try:
                self.a6.method_roles = ['tst']
                response = self.a6.execute(halo_request)
                eq_(1,2)
            except Exception as e:
                eq_(e.__class__, 'halo_aws.providers.cloud.aws.exceptions.ProviderError')

    def test_99998_aws_invoke_sync_success(self):
        app.config['PROVIDER'] = "AWS"
        app.config['CIRCUIT_BREAKER'] = False
        app.config['HALO_CONTEXT_LIST'] = ["CORRELATION"]
        app.config['SESSION_MINUTES'] = 30
        secret = '12345'
        app.config['SECRET_KEY'] = secret
        app.config['HALO_SECURITY_CLASS'] = 'tests.test_flask.Sec'
        public_id = '12345'
        hdr = HaloSecurity.user_token(None, public_id, 30, secret)
        headers = {'HTTP_HOST': '127.0.0.2', 'x-halo-access-token': hdr['token'],'x-halo-correlation-id':'123456'}
        with app.test_request_context(method='POST', path='/xst2/2/tst1/1/tst/0/', headers=headers):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            try:
                self.a5.method_roles = ['tst']
                response = self.a5.process(halo_request)
                eq_(response.code, 201)
            except Exception as e:
                print(str(e))
                eq_(1,2)

    def test_99999_aws_invoke_sync_success(self):
        app.config['PROVIDER'] = "AWS"
        app.config['DEBUG'] = True
        app.config['CIRCUIT_BREAKER'] = False
        app.config['HALO_CONTEXT_LIST'] = ["CORRELATION"]
        app.config['SESSION_MINUTES'] = 30
        secret = '12345'
        app.config['SECRET_KEY'] = secret
        app.config['HALO_SECURITY_CLASS'] = 'tests.test_flask.Sec'
        public_id = '12345'
        hdr = HaloSecurity.user_token(None, public_id, 30, secret)
        headers = {'HTTP_HOST': '127.0.0.2', 'x-halo-access-token': hdr['token'],'x-halo-correlation-id':'123456'}
        with app.test_request_context(method='POST', path='/xst2/2/tst1/1/tst/0/', headers=headers):
            halo_context = get_halo_context(request)
            halo_request = SysUtil.create_request(halo_context, "z1", request.args)
            try:
                self.a6.method_roles = ['tst']
                response = self.a6.execute(halo_request)
                eq_(response.code, 201)
            except Exception as e:
                print(str(e))
                eq_(1,2)