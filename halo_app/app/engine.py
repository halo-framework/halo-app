from __future__ import annotations

# python
import logging
import json
import re
from jsonpath_ng import parse
# aws
# common
# app
from halo_app.infra.exceptions import NoApiClassException, ApiException
from halo_app.app.exceptions import EngineException
from halo_app.app.context import HaloContext
from .result import Result
from ..const import HTTPChoice, ASYNC, BusinessEventCategory
from halo_app.exceptions import AbsHaloException
from ..reflect import Reflect
from halo_app.app.request import AbsHaloRequest, HaloEventRequest, HaloCommandRequest, HaloQueryRequest
from halo_app.app.response import AbsHaloResponse
from ..settingsx import settingsx
from ..classes import AbsBaseClass
from halo_app.infra.apis import ApiMngr
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


class ProcessingEngine(AbsBaseClass):

    def __init__(self,business_event,api=None):
        self.business_event = business_event
        self.api = api

    def set_back_api(self, halo_request,api):
        if api:
            foi_name = api["name"]
            foi_op = api["op"]
            foi_conn = api["conn"]
            #api = ApiMngr.get_api(foi_name)
            #instance = Reflect.instantiate(api, AbsBaseApi, halo_request.context)
            instance = ApiMngr.get_api_instance(foi_name, halo_request.context,foi_op)
            instance.conn = foi_conn
            return instance
        raise NoApiClassException("api class not defined")

    def set_api_headers(self,halo_request,api, seq=None, dictx=None):
        logger.debug("in set_api_headers ")
        if halo_request and api.api_type == "service":
            return dict(halo_request.headers)
        return {}
        raise AbsHaloException("no headers")

    def set_api_vars(self,halo_request,api, seq=None, dict=None):
        logger.debug("in set_api_vars " + str(halo_request))
        if True:
            ret = {}
            return ret
        raise AbsHaloException("no var")

    def set_api_auth(self,halo_request,api, seq=None, dict=None):
        return None

    def set_api_data(self,halo_request,api, seq=None, dict=None):
        return {}

    def execute_api(self,halo_request, back_api, back_vars, back_headers, back_auth, back_data=None, seq=None, dict=None):
        logger.debug("in execute_api "+back_api.name)
        if back_api:
            timeout = Util.get_timeout(halo_request.context)
            try:
                seq_msg = ""
                if seq:
                    seq_msg = "seq = " + seq + "."
                ret = back_api.run(timeout, headers=back_headers,auth=back_auth, data=back_data)
                msg = "in execute_api. " + seq_msg + " code= " + str(ret.status_code)
                logger.info(msg)
                return ret
            except ApiException as e:
                raise EngineException("failed to execute api:"+str(back_api.name),e)
        return None

    def extract_json(self,halo_request,api, back_response, seq=None):
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
                    raise AbsHaloException("mapping error for " + halo_request.method_id, e)
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
        raise AbsHaloException("no mapping for " + halo_request.method_id)

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


    def do_operation_1(self, halo_request)->Result:  # basic maturity - single request
        logger.debug("do_operation_1")
        # 1. get api definition to access the BANK API  - url + vars dict
        if self.business_event.EVENT_CATEGORY == BusinessEventCategory.EMPTY:
            back_api = self.api
        else:
            api = self.business_event.get()['1']
            back_api = self.set_back_api(halo_request,api)
        # 2. array to store the headers required for the API Access
        back_headers = self.set_api_headers(halo_request,back_api)
        # 3. Set request params
        back_vars = self.set_api_vars(halo_request,back_api)
        # 4. Set request auth
        back_auth = self.set_api_auth(halo_request,back_api)
        # 5. Set request view
        back_data = self.set_api_data(halo_request,back_api)
        # 6. Sending the request to the BANK API with params
        back_response = self.execute_api(halo_request, back_api, back_vars, back_headers, back_auth,
                                                   back_data)
        # 7. extract from Response stored in an object built as per the BANK API Response body JSON Structure
        back_json = self.extract_json(halo_request,back_api, back_response)
        payload = {'1': back_json}
        # 8. return json response
        return Result.ok(payload)

    def do_operation_2(self, halo_request)->Result:  # medium maturity - foi
        logger.debug("do_operation_2")
        api_list = []
        dict = {}
        for seq in self.business_event.keys():
            print("seq="+str(seq))
            # 1. get get first order interaction
            foi = self.business_event.get(seq)
            # 2. get api definition to access the BANK API  - url + vars dict
            back_api = self.set_back_api(halo_request, foi)
            api_list.append(back_api)
            if back_api.conn == ASYNC:
                # 2.1 do async api work
                back_json = self.do_api_async_work(halo_request, back_api, seq, dict)
            else:
                # 2.2 do api work
                back_json = self.do_api_work(halo_request, back_api, seq, dict)
            # 3. store in dict
            dict[seq] = back_json
        for api in api_list:
            api.terminate()
        return Result.ok(dict)

    def do_api_async_work(self, halo_request, back_api, seq, dict=None):
        # 3. array to store the headers required for the API Access
        back_headers = self.set_api_headers(halo_request,back_api, seq, dict)
        # 4. set vars
        back_vars = self.set_api_vars(halo_request,back_api, seq, dict)
        # 5. auth
        back_auth = self.set_api_auth(halo_request,back_api, seq, dict)
        # 6. set request view
        back_data = self.set_api_data(halo_request,back_api, seq, dict)
        # 7. Sending the request to the BANK API with params
        status = get_provider().add_to_queue(halo_request, back_api, back_vars, back_headers, back_auth,
                                         back_data, seq, dict)
        return {}

    def do_api_work(self,halo_request, back_api, seq, dict=None):
        # 3. array to store the headers required for the API Access
        back_headers = self.set_api_headers(halo_request,back_api, seq, dict)
        # 4. set vars
        back_vars = self.set_api_vars(halo_request,back_api, seq, dict)
        # 5. auth
        back_auth = self.set_api_auth(halo_request,back_api, seq, dict)
        # 6. set request view
        back_data = self.set_api_data(halo_request,back_api, seq, dict)
        # 7. Sending the request to the BANK API with params
        back_response = self.execute_api(halo_request, back_api, back_vars, back_headers, back_auth,
                                              back_data, seq, dict)
        # 8. extract from Response stored in an object built as per the BANK API Response body JSON Structure
        back_json = self.extract_json(halo_request,back_api, back_response, seq)
        # return
        return back_json

    def set_api_op(self, api, payload):
        req = payload['request']
        #if not req.sub_func:# base option
            #if req.request.method == HTTPChoice.put.value:
                #if payload['state'] == 'BookHotel':
                #    api.op = HTTPChoice.post.value
                # if payload['state'] == 'BookCancel':
                #    api.op = HTTPChoice.delete.value
        #else:
            #if req.sub_func == "deposit":
                # if req.request.method == HTTPChoice.put.value:
                    # if payload['state'] == 'BookHotel':
                    #    api.op = HTTPChoice.post.value
                    # if payload['state'] == 'BookCancel':
                    #    api.op = HTTPChoice.delete.value
        return api

    def do_saga_work(self, api, results, payload):
        logger.debug("do_saga_work=" + str(api) + " result=" + str(results) + "payload=" + str(payload))
        set_api = self.set_api_op(api,payload)
        return self.do_api_work(payload['request'], set_api, payload['seq'])

    def do_operation_3(self, halo_request)->Result:  # high maturity - saga transactions
        logger.debug("do_operation_3")
        sagax = load_saga("test",halo_request, self.business_event.get_saga(), settings.SAGA_SCHEMA)
        payloads = {}
        apis = {}
        counter = 1
        for state in self.business_event.get_saga()["States"]:
            if 'Resource' in self.business_event.get_saga()["States"][state]:
                api_name = self.business_event.get_saga()["States"][state]['Resource']
                logger.debug(api_name)
                payloads[state] = {"request": halo_request, 'seq': str(counter),"state":state}
                apis[state] = self.do_saga_work
                counter = counter + 1

        try:
            ret = sagax.execute(halo_request.context, payloads, apis)
            return Result.ok(ret)
        except SagaRollBack as e:
            raise ApiException(e.message,e,e.detail ,e.data,status_code=500)







