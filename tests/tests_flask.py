from __future__ import print_function

import json
import os

from faker import Faker
from flask import Flask, request
from flask_restful import Api
from nose.tools import eq_
from jsonpath_ng import jsonpath, parse

from halo_flask.flask.utilx import Util, status
from halo_flask.flask.mixinx import AbsApiMixinX,PerfMixinX
from halo_flask.flask.viewsx import PerfLinkX
from halo_flask.exceptions import ApiError
from halo_flask.logs import log_json
from halo_flask import saga
from halo_flask.const import HTTPChoice
from halo_flask.apis import CnnApi,GoogleApi,TstApi
from halo_flask.flask.viewsx import Resource,AbsBaseLinkX
import unittest



fake = Faker()
app = Flask(__name__)
api = Api(app)

from halo_flask.request import HaloRequest
from halo_flask.response import HaloResponse


class A1(AbsApiMixinX):

    def set_back_api(self,halo_request, foi=None):
        if not foi:#not in seq
            if not halo_request.behavior_qualifier:#not in bq
                if halo_request.request.method == HTTPChoice.delete.value:
                    return CnnApi(Util.get_req_context(halo_request.request),HTTPChoice.delete.value)
        return super(A1,self).set_back_api(halo_request,foi)

    def extract_json(self,halo_request, back_response, seq=None):
        if seq == None:#no event
            if halo_request.request.method == HTTPChoice.get.value:#method type
                return {"tst_get":"good"}
            if halo_request.request.method == HTTPChoice.delete.value:#method type
                return {"tst_delete":"good"}
        else:#in event
            if halo_request.request.method == HTTPChoice.put.value:#method type
                if seq == '1':
                    return {"tst_put":"good1"}
                if seq == '2':
                    return {"tst_put":"good2"}
            if halo_request.request.method == HTTPChoice.post.value:#method type
                if seq == '1':
                    return {"tst_post":"good1"}
                if seq == '2':
                    return {"tst_post":"good2"}
            if halo_request.request.method == HTTPChoice.patch.value:#method type
                return {"tst_patch":"good"}


class A2(Resource, A1, AbsBaseLinkX):
    def set_api_headers_deposit(self,halo_request, seq=None, dict=None):
        return super(A2,self).set_api_headers(halo_request, seq, dict)

    def set_api_vars_deposit(self,halo_request, seq=None, dict=None):
        return super(A2,self).set_api_vars(halo_request, seq, dict)

    def set_api_auth_deposit(self,halo_request, seq=None, dict=None):
        return super(A2,self).set_api_auth(halo_request, seq, dict)

    def set_api_data_deposit(self,halo_request, seq=None, dict=None):
        return super(A2,self).set_api_data(halo_request, seq, dict)

    def execute_api_deposit(self,halo_request, back_api, back_vars, back_headers, back_auth, back_data=None, seq=None, dict=None):
        return super(A2,self).execute_api(halo_request, back_api, back_vars, back_headers, back_auth, back_data, seq, dict)

    def extract_json_deposit(self,halo_request, back_response, seq=None):
        if seq == None:#no event
            if halo_request.request.method == HTTPChoice.get.value:#method type
                return {"tst_get_deposit":"good"}
            if halo_request.request.method == HTTPChoice.delete.value:#method type
                return {"tst_delete_deposit":"good"}
        else:#in event
            if halo_request.request.method == HTTPChoice.put.value:#method type
                if seq == '1':
                    return {"tst_put_deposit":"good1"}
                if seq == '2':
                    return {"tst_put_deposit":"good2"}
            if halo_request.request.method == HTTPChoice.post.value:#method type
                if seq == '1':
                    return {"tst_post_deposit":"good1"}
                if seq == '2':
                    return {"tst_post_deposit":"good2"}
            if halo_request.request.method == HTTPChoice.patch.value:#method type
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


class P1(PerfMixinX):
    pass

class P2(PerfLinkX):
    pass




class TestUserDetailTestCase(unittest.TestCase):
    """
    Tests /users detail operations.
    """

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
        self.p1 = P1()
        self.p2 = P2()


    def test_1_get_request_returns_exception(self):
        with app.test_request_context(method='GET', path='/?abc=def'):
            try:
                response = self.a1.process_get(request, {})
                raise False
            except Exception as e:
                eq_(e.__class__.__name__, "NoApiClassException")

    def test_2_delete_request_returns_dict(self):
        with app.test_request_context(method='DELETE', path='/?abc=def'):
            response = self.a1.process_delete(request, {})
            eq_(response.payload, {1: {"tst_delete":"good"}})

    def test_3_put_request_returns_dict(self):
        with app.test_request_context(method='PUT', path='/?abc=def'):
            response = self.a1.process_put(request, {})
            eq_(response.payload, {'1': {'tst_put': 'good1'}, '2': {'tst_put': 'good2'}})

    def test_4_post_request_returns_a_given_string(self):
        with app.test_request_context(method='POST', path='/?abc=def'):
            response = self.a1.process_post(request, {})
            print("response=" + str(response.payload))
            eq_(response.code, status.HTTP_201_CREATED)
            eq_(response.payload, {'$.BookHotelResult': {'tst_post': 'good1'}, '$.BookFlightResult': {'tst_post': 'good2'}, '$.BookRentalResult': None})

    def test_5_patch_request_returns_a_given_string(self):
        with app.test_request_context(method='PATCH', path='/?abc=def'):
            response = self.a1.process_patch(request, {})
            print("response=" + str(response.payload))
            eq_(response.code, status.HTTP_200_OK)
            eq_(response.payload, {'$.BookHotelResult': {'tst_patch': 'good'}, '$.BookFlightResult': {'tst_patch': 'good'}, '$.BookRentalResult': {'tst_patch': 'good'}})

    def test_6_api_request_returns_a_CircuitBreakerError(self):
        with app.test_request_context(method='GET', path='/?a=b'):
            api = CnnApi(Util.get_req_context(request))
            timeout = Util.get_timeout(request)
            try:
                response = api.get(timeout)
                assert False
            except ApiError as e:
                #eq_(e.status_code, status.HTTP_403_NOT_FOUND)
                eq_(e.__class__.__name__,"CircuitBreakerError")


    def test_7_api_request_returns_a_given_CircuitBreakerError2(self):
        with app.test_request_context(method='GET', path='/?a=b'):
            api = TstApi(Util.get_req_context(request))
            timeout = Util.get_timeout(request)
            try:
                response = api.get(timeout)
                assert False
            except ApiError as e:
                #eq_(e.status_code, status.HTTP_403_NOT_FOUND)
                eq_(e.__class__.__name__,"CircuitBreakerError")

    def test_8_api_request_returns_a_fail(self):
        with app.test_request_context(method='GET', path='/?a=b'):
            api = CnnApi(Util.get_req_context(request))
            api.url = api.url + "/lgkmlgkhm??l,mhb&&,g,hj "
            timeout = Util.get_timeout(request)
            try:
                response = api.get(timeout)
                assert False
            except ApiError as e:
                eq_(e.status_code, status.HTTP_404_NOT_FOUND)
                #eq_(e.__class__.__name__,"CircuitBreakerError")

    def test_9_send_event(self):
        with app.test_request_context(method='GET', path='/?a=b'):
            from halo_flask.events import AbsBaseEvent
            class Event1Event(AbsBaseEvent):
                target_service = 'func1'
                key_name = 'def'
                key_val = '456'

            event = Event1Event()
            dict = {"name": "david"}
            response = event.send_event(dict)
            print("event response " + str(response))
            eq_(response, 'sent event')

    def test_91_system_debug_enabled(self):
        with app.test_request_context(method='GET', path='/?a=b'):
            os.environ['DEBUG_LOG'] = 'true'
            flag = 'false'
            for i in range(0, 80):
                ret = Util.get_system_debug_enabled()
                print(ret)
                if ret == 'true':
                    flag = ret
            eq_(flag, 'true')

    def test_92_debug_enabled(self):
        header = {'HTTP_DEBUG_LOG_ENABLED': 'true'}
        with app.test_request_context(method='GET', path='/?a=b', headers=header):
            ret = Util.get_req_context(request)
            eq_(ret["debug-log-enabled"], 'true')

    def test_93_json_log(self):
        import traceback
        header = {'HTTP_DEBUG_LOG_ENABLED': 'true'}
        with app.test_request_context(method='GET', path='/?a=b', headers=header):
            req_context = Util.get_req_context(request)
            try:
                raise Exception("test it")
            except Exception as e:
                e.stack = traceback.format_exc()
                ret = log_json(req_context, {"abc": "def"}, err=e)
                print(str(ret))
                eq_(ret["debug-log-enabled"], 'true')

    def test_94_get_request_with_debug(self):
        header = {'HTTP_DEBUG_LOG_ENABLED': 'true'}
        with app.test_request_context(method='GET', path='/?a=b', headers=header):
            ret = Util.get_debug_enabled(request)
            eq_(ret, 'true')

    def test_95_debug_event(self):
        event = {'debug-log-enabled': 'true'}
        ret = Util.get_correlation_from_event(event)
        eq_(Util.event_req_context["debug-log-enabled"], 'true')
        ret = Util.get_correlation_from_event(event)
        eq_(ret["debug-log-enabled"], 'true')

    def test_96_pref_mixin(self):
        with app.test_request_context(method='GET', path='/perf'):
            response = self.p1.process_get(request, {})
            eq_(response.code, status.HTTP_200_OK)

    def test_97_pref_mixin1(self):
        with app.test_request_context(method='GET', path='/perf/tst'):
            response = self.p2.get()
            eq_(response.status_code, status.HTTP_200_OK)

    def test_98_run_simple_delete(self):
        with app.test_request_context(method='DELETE', path="/start"):
            response = self.a2.delete()
            eq_(response.status_code, status.HTTP_200_OK)

    def test_990_run_seq_get(self):
        with app.test_request_context(method='GET', path="/"):
            response = self.a2.get()
            eq_(response.status_code, status.HTTP_200_OK)

    def test_991_load_saga(self):
        with open("../env/config/saga.json") as f:
            jsonx = json.load(f)
        sagax = saga.load_saga("test", jsonx, app.config['SAGA_SCHEMA'])
        eq_(len(sagax.actions), 6)

    def test_9920_run_saga(self):
        with app.test_request_context(method='POST', path="/"):
            response = self.a2.post()
            eq_(response.status_code, status.HTTP_201_CREATED)

    def test_9921_run_saga_bq(self):
        with app.test_request_context(method='POST', path="/tst?behavior_qualifier=deposit"):
            response = self.a2.post()
            eq_(response.status_code, status.HTTP_201_CREATED)

    def test_9922_run_saga_bq_error(self):
        with app.test_request_context(method='POST', path="/tst?behavior_qualifier=tst"):
            try:
                response = self.a2.post()
                raise False
            except Exception as e:
                eq_(e.__class__.__name__, "InternalServerError")

    def test_9923_trans_json(self):
        with app.test_request_context(method='GET', path="/tst"):
            try:
                response = self.a2.get()
                raise False
            except Exception as e:
                eq_(e.__class__.__name__, "InternalServerError")

    def test_9930_rollback_saga(self):
        with app.test_request_context(method='PUT', path="/"):
            try:
                response = self.a2.process_put(request, {})
                assert False
            except Exception as e:
                eq_(e.__class__.__name__, "ServerError")

    def test_9931_rollback_saga_error(self):
        with app.test_request_context(method='PATCH', path="/"):
            try:
                response = self.a2.process_patch(request, {})
                assert False
            except Exception as e:
                eq_(e.__class__.__name__, "SagaError")


    def test_9932_all_rollback_saga(self):
        with app.test_request_context(method='PUT', path="/"):
            try:
                response = self.a2.put()
                assert False
            except Exception as e:
                eq_(e.__class__.__name__, "InternalServerError")

    def test_9933_all_rollback_saga_bq(self):
        with app.test_request_context(method='PUT', path="/test?behavior_qualifier=deposit"):
            try:
                response = self.a2.put()
                assert False
            except Exception as e:
                eq_(e.__class__.__name__, "InternalServerError")

    def test_9940_ssm_aws(self):  # @TODO test without HALO_AWS
        header = {'HTTP_HOST': '127.0.0.2'}
        with app.test_request_context(method='GET', path='/?a=b', headers=header):
            try:
                from halo_flask.ssm import set_app_param_config
                set_app_param_config("AWS", "124")
                from halo_flask.ssm import get_app_config
                config = get_app_config("AWS")
                eq_(config.get_param("halo_flask")["url"], 'https://127.0.0.1:8000/loc')
            except Exception as e:
                eq_(e.__class__.__name__, "ProviderError")

    def test_9941_ssm_aws(self):  # @TODO test with HALO_AWS
        header = {'HTTP_HOST': '127.0.0.2'}
        with app.test_request_context(method='GET', path='/?a=b', headers=header):
            from halo_flask.ssm import set_app_param_config
            set_app_param_config("AWS", "124")
            from halo_flask.ssm import get_app_config
            config = get_app_config("AWS")
            eq_(config.get_param("halo_flask")["url"], 'https://127.0.0.1:8000/loc')

    def test_995_ssm_onperm(self):  # @TODO
        header = {'HTTP_HOST': '127.0.0.2'}
        app.config['SSM_TYPE'] = "ONPREM"
        app.config['ONPREM_SSM_CLASS_NAME'] = 'OnPremClient'
        app.config['ONPREM_SSM_MODULE_NAME'] = 'halo_flask.providers.ssm.onprem_ssm_client'
        with app.test_request_context(method='GET', path='/?a=b', headers=header):
            from halo_flask.ssm import set_app_param_config
            set_app_param_config("ONPREM", "124")
            from halo_flask.ssm import get_app_config
            config = get_app_config("ONPREM")
            t = config.get_param('halo_flask')
            print("t="+str(t))
            eq_(str(t), '<Section: DEFAULT>')

    def test_996_error_handler(self):
        with app.test_request_context(method='DELETE', path='/perf'):
            response = self.p1.process_delete(request, {})
            #print("x="+str(response.content))
            #print("ret=" + str(json.loads(response.content)))
            #eq_(json.loads(response.content)['error']['error_message'], 'test error msg')
            eq_(response.code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_997_timeout(self):
        with app.test_request_context(method='GET', path='/?a=b'):
            os.environ["AWS_LAMBDA_FUNCTION_NAME"] = "halo_flask"
            timeout = Util.get_timeout(request)
            eq_(timeout, 3)



    def test_998_perf_get(self):
        with app.test_request_context(method='GET', path='/perf'):
            response = self.p1.process_get(request, {})
            eq_(response.code, status.HTTP_200_OK)

    def test_999_perf_get_link(self):
        with app.test_request_context(method='GET', path='/perf'):
            response = self.p2.get()
            eq_(response.status_code, status.HTTP_200_OK)



