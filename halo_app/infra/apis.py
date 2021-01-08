from __future__ import print_function

# python
import datetime
import logging
import uuid
import json
from abc import ABCMeta
import requests
from halo_app.providers.providers import get_provider,ProviderError
from halo_app.classes import AbsBaseClass
from halo_app.exceptions import MaxTryHttpException, ApiError, NoApiDefinitionError, \
    HaloMethodNotImplementedException, MissingClassConfigError, IllegalMethodException
from halo_app.logs import log_json
from halo_app.reflect import Reflect
from halo_app.app.utilx import Util
from halo_app.const import HTTPChoice, SYSTEMChoice, LOGChoice
from halo_app.settingsx import settingsx

settings = settingsx()

Rest = "rest"
Soap = "soap"
Rpc = "rpc"

logger = logging.getLogger(__name__)


class AbsResponse(AbsBaseClass):
    content = None
    headers = None
    status_code = None

    def __init__(self, content, headers={},status_code=200):
        self.content = content
        self.headers = headers
        self.status_code = status_code

class SoapResponse(AbsResponse):
    pass

class ProviderResponse(SoapResponse):
    pass

class AbsBaseApi(AbsBaseClass):
    __metaclass__ = ABCMeta

    name = None
    op = HTTPChoice.get.value
    url = None
    api_type = None
    protocol = None
    halo_context = None
    #cb = MyCircuitBreaker()
    session = None
    version = None

    def __init__(self, halo_context, method=None,session=None):
        self.halo_context = halo_context
        if method:
            self.op = method
        self.url, self.api_type,self.protocol = self.get_url_str()
        self.version = self.get_version()
        if session:
            self.session = session
        else:
            self.session = requests.session()

    def get_url_str(self):
        """

        :return:
        """
        api_config = settings.API_CONFIG
        logger.debug("api_config: " + str(api_config), extra=log_json(self.halo_context))
        if api_config and self.name in api_config:
            url = api_config[self.name]["url"]
            type = api_config[self.name]["type"]
            protocol = "rest"
            if "protocol" in api_config[self.name]:
                protocol = api_config[self.name]["protocol"]
            return url,type,protocol

        raise NoApiDefinitionError(self.name)

    def get_version(self):
        """

        :return:
        """
        api_config = settings.API_CONFIG
        version = '$LATEST'
        if api_config and self.name in api_config:
            if  "version" in api_config[self.name]:
                version = api_config[self.name]["version"]
        return version

    def terminate(self):
        if self.session:
            print("terminate session:"+str(self.session))
            self.session.close()
            self.session = None

    def provider_invoke(self,halo_context, method, url, api_type, timeout, data=None, headers=None, auth=None):

        try:
            service_name = self.name
            logger.debug("send invoke to target_service:" + service_name, extra=log_json(halo_context))
            if data:
                x = str(data.decode('utf8').replace("'", '"'))
                if x != "":
                    datax = json.loads(x)
                    datay = json.dump(datax)
                else:
                    datay = ""
            else:
                datay = ""
            messageDict = {"method":method,"url":url,"views":datay,"headers":headers,"auth":auth}
            print("messageDict="+str(messageDict)+" version:"+self.version)
            ret = get_provider().invoke_sync(halo_context,messageDict,service_name,version=self.version)
            print("ret:"+str(ret))
            content = json.loads(ret['Payload'].read())
            print("content:" + str(content))
            provider_response = ProviderResponse(content["body"],ret['ResponseMetadata']["HTTPHeaders"],ret['StatusCode'])
            return provider_response
        except ProviderError as e:
            logger.error("Unexpected Provider Error", extra=log_json(halo_context, messageDict, e))
            raise e


class AbsRestApi(AbsBaseApi):
    __metaclass__ = ABCMeta

    def __init__(self,halo_context, method=None,session=None):
        super(AbsRestApi,self).__init__(halo_context,method,session)

    def do_request(self, method, url, timeout, data=None, headers=None, auth=None):
        if not self.session:
            self.session = requests.session()
        return self.session.request(method, url, data=data, headers=headers,
                                timeout=timeout, auth=auth)

    def exec_client(self, halo_context, method, url, api_type, timeout, data=None, headers=None, auth=None):
        """

        :param halo_context:
        :param method:
        :param url:
        :param api_type:
        :param timeout:
        :param data:
        :param headers:
        :return:
        """

        if api_type == 'service':
            return self.provider_invoke(halo_context, method, url, api_type, timeout, data, headers, auth)

        msg = "Max Try for url: ("+str(settings.HTTP_MAX_RETRY)+") " + str(url)
        for i in range(0, settings.HTTP_MAX_RETRY):
            logger.debug("try index: " + str(i), extra=log_json(halo_context))
            try:
                logger.debug("try: " + str(i), extra=log_json(halo_context))
                ret = self.do_request(method, url, timeout, data=data, headers=headers, auth=auth)
                logger.debug("request status_code=" + str(ret.status_code) +" content=" + str(ret.content), extra=log_json(halo_context))
                if ret.status_code >= 500:
                    continue
                if 200 > ret.status_code or 500 > ret.status_code >= 300:
                    err = ApiError("error status_code " + str(ret.status_code) + " in : " + url)
                    err.status_code = ret.status_code
                    err.stack = None
                    raise err
                return ret
            except requests.exceptions.ReadTimeout as e:  # this confirms you that the request has reached server
                logger.debug(str(e))
                logger.debug(
                    "ReadTimeout " + str(
                        settings.SERVICE_READ_TIMEOUT_IN_MS) + " in method=" + method + " for url=" + url,
                    extra=log_json(halo_context))
                continue
            except requests.exceptions.ConnectTimeout as e:
                logger.debug(str(e))
                logger.debug("ConnectTimeout in method=" + str(
                    settings.SERVICE_CONNECT_TIMEOUT_IN_MS) + " in method=" + method + " for url=" + url,
                             extra=log_json(halo_context))
                continue
        raise MaxTryHttpException(msg)

    def set_api_url(self, key, val):
        """

        :param key:
        :param val:
        :return:
        """
        strx = self.url
        strx = strx.replace("$" + str(key), str(val))
        logger.debug("url replace var: " + strx, extra=log_json(self.halo_context))
        self.url = strx
        return self.url

    def set_api_base(self, base_url):
        """

        :param query:
        :return:
        """
        strx = self.url
        if "base_url" in self.url:
            strx = strx.replace("base_url",base_url)
        logger.debug("url add base: " + strx, extra=log_json(self.halo_context))
        self.url = strx
        return self.url

    def set_api_query(self, query):
        """

        :param query:
        :return:
        """
        strx = self.url
        if "?" in self.url:
            strx = strx + "&" + query
        else:
            strx = strx + "?" + query
        logger.debug("url add query: " + strx, extra=log_json(self.halo_context))
        self.url = strx
        return self.url

    def set_api_params(self, params):
        """

        :param params:
        :return:
        """
        if not params or len(params) == 0:
            return self.url
        strx = self.url
        for key in params:
            val = params[key]
            query = key+"="+val
            if "?" in self.url:
                strx = strx + "&" + query
            else:
                strx = strx + "?" + query
        logger.debug("url add query: " + strx, extra=log_json(self.halo_context))
        self.url = strx
        return self.url

    def process(self, method, url, timeout, data=None, headers=None,auth=None):
        """

        :param method:
        :param url:
        :param timeout:
        :param data:
        :param headers:
        :return:
        """
        return self.process_rest(method, url, timeout, data, headers,auth)

    def get_vars_from_url(self,url):
        import urllib.parse as urlparse
        from urllib.parse import parse_qs
        parsed = urlparse.urlparse(url)
        return parse_qs(parsed.query)

    def process_rest(self, method, url, timeout, data=None, headers=None,auth=None):
        """

        :param method:
        :param url:
        :param timeout:
        :param data:
        :param headers:
        :return:
        """
        try:
            logger.debug("Api name: " + self.name +" method: " + str(method) + " url: " + str(url) + " headers:" + str(headers), extra=log_json(self.halo_context))
            now = datetime.datetime.now()
            ret = self.exec_client(self.halo_context, method, url, self.api_type, timeout, data=data, headers=headers, auth=auth)
            total = datetime.datetime.now() - now
            logger.info(LOGChoice.performance_data.value, extra=log_json(self.halo_context,
                                                                         {LOGChoice.type.value: SYSTEMChoice.api.value, LOGChoice.milliseconds.value: int(total.total_seconds() * 1000),
                                                       LOGChoice.url.value: str(url)}))
            logger.debug("ret: " + str(ret), extra=log_json(self.halo_context))
            return ret
        except requests.ConnectionError as e:
            msg = str(e)
            logger.debug("error: " + msg, extra=log_json(self.halo_context))
            er = ApiError(msg,e)
            er.status_code = 500
            raise er
        except requests.HTTPError as e:
            msg = str(e)
            logger.debug("error: " + msg, extra=log_json(self.halo_context))
            er = ApiError(msg,e)
            er.status_code = 500
            raise er
        except requests.Timeout as e:
            msg = str(e)
            logger.debug("error: " + msg, extra=log_json(self.halo_context))
            er = ApiError(msg,e)
            er.status_code = 500
            raise er
        except requests.RequestException as e:
            msg = str(e)
            logger.debug("error: " + msg, extra=log_json(self.halo_context))
            er = ApiError(msg,e)
            er.status_code = 500
            raise er
        except ApiError as e:
            msg = str(e)
            logger.debug("error: " + msg, extra=log_json(self.halo_context))
            raise e

    def run(self,timeout, headers=None, auth=None,data=None):
        if headers is None:
            headers = headers
        return self.process(self.op, self.url, timeout, headers=headers,auth=auth,data=data)

    def get(self, timeout, headers=None,auth=None):
        """

        :param timeout:
        :param headers:
        :return:
        """
        if headers is None:
            headers = headers
        return self.process(HTTPChoice.get.value, self.url, timeout, headers=headers,auth=auth)

    def post(self, data, timeout, headers=None,auth=None):
        """

        :param data:
        :param timeout:
        :param headers:
        :return:
        """
        logger.debug("payload=" + str(data))
        if headers is None:
            headers = headers
        return self.process(HTTPChoice.post.value, self.url, timeout, data=data, headers=headers,auth=auth)

    def put(self, data, timeout, headers=None,auth=None):
        """

        :param data:
        :param timeout:
        :param headers:
        :return:
        """
        if headers is None:
            headers = headers
        return self.process(HTTPChoice.put.__str__(), self.url, timeout, data=data, headers=headers,auth=auth)

    def patch(self, data, timeout, headers=None,auth=None):
        """

        :param data:
        :param timeout:
        :param headers:
        :return:
        """
        if headers is None:
            headers = headers
        return self.process(HTTPChoice.patch.value, self.url, timeout, data=data, headers=headers,auth=auth)

    def delete(self, timeout, headers=None,auth=None):
        """

        :param timeout:
        :param headers:
        :return:
        """
        if headers is None:
            headers = headers
        return self.process(HTTPChoice.delete.value, self.url, timeout, headers=headers,auth=auth)

    def fwd_process(self, typer, request, vars, headers,auth=None):
        """

        :param typer:
        :param request:
        :param vars:
        :param headers:
        :return:
        """
        verb = typer.value
        if verb == HTTPChoice.get.value or HTTPChoice.delete.value:
            data = None
        else:
            data = request.data
        return self.process(verb, self.url, Util.get_timeout(request), data=data, headers=headers,auth=auth)

class AbsSoapApi(AbsBaseApi):
    __metaclass__ = ABCMeta

    def __init__(self,halo_context, method=None,session=None):
        super(AbsSoapApi,self).__init__(halo_context,method,session)

    def do_request(self,method,timeout, data=None, headers=None, auth=None):
        return self.exec_soap(method,timeout, data, headers, auth)


    def run(self,timeout,data ,headers=None,auth=None):
        """

        :param data:
        :param timeout:
        :param headers:
        :return:
        """
        if headers is None:
            headers = headers
        return self.process(self.op,self.url,timeout, data=data, headers=headers,auth=auth)

    def process(self,method,url, timeout, data=None, headers=None, auth=None):
        from zeep import Client,Transport
        try:
            logger.debug(
                "Api name: " + self.name  + " url: " + str(url) + " headers:" + str(headers),
                extra=log_json(self.halo_context))
            now = datetime.datetime.now()
            transport = Transport(session=self.session, timeout=timeout, operation_timeout=timeout)
            self.client = Client(url,transport=transport)
            soap_response = self.do_request(method,timeout, data, headers, auth)
            total = datetime.datetime.now() - now
            logger.info(LOGChoice.performance_data.value, extra=log_json(self.halo_context,
                                                                         {LOGChoice.type.value: SYSTEMChoice.api.value,
                                                                          LOGChoice.milliseconds.value: int(
                                                                              total.total_seconds() * 1000),
                                                                          LOGChoice.url.value: str(url)}))
            logger.debug("ret: " + str(soap_response), extra=log_json(self.halo_context))
            return soap_response
        except ApiError as e:
            msg = str(e)
            logger.debug("error: " + msg, extra=log_json(self.halo_context))
            raise e

    def exec_soap(self,method,timeout, data=None, headers=None, auth=None):
        if method is None:
            raise IllegalMethodException("missing method value")
        logger.debug("method="+str(method))
        try:
            soap_response = getattr(self, 'do_%s' % method)(timeout, data, headers, auth)
            if type(soap_response) == SoapResponse:
                return soap_response
        except AttributeError as ex:
            raise HaloMethodNotImplementedException("function for "+str(method),ex)

"""
Request api but don't wait for response
try:
    requests.get("http://127.0.0.1:8000/api/",timeout=10)
except requests.exceptions.ReadTimeout: #this confirms you that the request has reached server
    do_something
except:
    print "unable to reach server"
    raise
"""

from threading import RLock
from halo_app.app.context import HaloContext
lock = RLock()
api_dict = {}
class ApiMngr(AbsBaseClass):

    global HALO_API_LIST

    def __init__1(self, halo_context):
        logger.debug("ApiMngr=" + str(halo_context))
        self.halo_context = halo_context

    def set_api_list1(self,list):
        """

        :param name:
        :return:
        """
        logger.debug("set_api_list")
        if list:
            self.API_LIST = list

    @staticmethod
    def get_api(name):
        """

        :param name:
        :return:
        """
        logger.debug("get_api=" + name)
        if name in HALO_API_LIST:
            class_name = HALO_API_LIST[name]
            if class_name:
                return class_name
            #else:

        raise NoApiDefinitionError(name)

    @staticmethod
    def get_api_instance(name:str,ctx:HaloContext,method:str="", *args):
        global api_dict
        #ctx = args[0]
        id = None
        if HaloContext.items[HaloContext.CORRELATION] in ctx.keys():
            id = ctx.get(HaloContext.items[HaloContext.CORRELATION])
            logger.debug("ctx:"+str(id))
        if not id:
            id = str(uuid.uuid4())[:8]
        if name in HALO_API_LIST:
            class_name = HALO_API_LIST[name]
            if class_name+id in api_dict:
                return api_dict[class_name+id]
            else:
                session = requests.session()
                params = []
                params.append(ctx)
                params.append(method)
                params.append(session)
                for x in args:
                    params.append(x)
                api = Reflect.instantiate(class_name, AbsBaseApi, *params)
                lock.acquire()
                try:
                    api_dict[class_name+id] = api
                finally:
                    lock.release()
                return api
        raise NoApiDefinitionError(name)

HALO_API_LIST = None
SSM_CONFIG = None
SSM_APP_CONFIG = None
def load_api_config(stage_type,ssm_type,func_name,API_CONFIG):
    global HALO_API_LIST
    global SSM_CONFIG
    global SSM_APP_CONFIG

    from halo_app.ssm import get_config

    SSM_CONFIG = get_config(ssm_type)
    # set_param_config(AWS_REGION, 'DEBUG_LOG', '{"val":"false"}')
    # SSM_CONFIG.get_param("test")


    from halo_app.ssm import get_app_config

    SSM_APP_CONFIG = get_app_config(ssm_type)

    # api_config:{'About': {'url': 'http://127.0.0.1:7000/about/', 'type': 'api'}, 'Task': {'url': 'http://127.0.0.1:7000/task/$upcid/', 'type': 'api'}, 'Curr': {'url': 'http://127.0.0.1:7000/curr/', 'type': 'api'}, 'Top': {'url': 'http://127.0.0.1:7000/top/', 'type': 'api'}, 'Rupc': {'url': 'http://127.0.0.1:7000/upc/$upcid/', 'type': 'api'}, 'Upc': {'url': 'http://127.0.0.1:7000/upc/$upcid/', 'type': 'api'}, 'Contact': {'url': 'http://127.0.0.1:7000/contact/', 'type': 'api'}, 'Fail': {'url': 'http://127.0.0.1:7000/fail/', 'type': 'api'}, 'Rtask': {'url': 'http://127.0.0.1:7000/task/$upcid/', 'type': 'api'}, 'Page': {'url': 'http://127.0.0.1:7000/page/$upcid/', 'type': 'api'}, 'Sim': {'url': 'http://127.0.0.1:7000/sim/', 'type': 'api'}, 'Google': {'url': 'http://www.google.com', 'type': 'service'}}
    for item in SSM_APP_CONFIG.cache.items:
        if item not in [func_name, 'DEFAULT']:
            url = SSM_APP_CONFIG.get_param(item)["url"]
            logger.debug(item + ":" + url)
            for key in API_CONFIG:
                current = API_CONFIG[key]
                type = current["type"]
                if type == "service":
                    continue
                new_url = current["url"]
                if "service://" + item in new_url:
                    API_CONFIG[key]["url"] = new_url.replace("service://" + item, url)
    logger.debug(str(API_CONFIG))
    api_list = {}
    if API_CONFIG:
        for key in API_CONFIG:
            if "class" in API_CONFIG[key]:
                class_name = API_CONFIG[key]["class"]
                api_list[key] = class_name
            else:
                raise MissingClassConfigError(key)

    HALO_API_LIST = api_list
    #ApiMngr.instance().set_api_list(api_list)

"""
def fullname(o):
  # o.__module__ + "." + o.__class__.__qualname__ is an example in
  # this context of H.L. Mencken's "neat, plausible, and wrong."
  # Python makes no guarantees as to whether the __module__ special
  # attribute is defined, so we take a more circumspect approach.
  # Alas, the module name is explicitly excluded from __qualname__
  # in Python 3.

  module = o.__class__.__module__
  if module is None or module == str.__class__.__module__:
    return o.__class__.__name__  # Avoid reporting __builtin__
  else:
    return module + '.' + o.__class__.__name__

def get_rest_api_instance(class_name,*args):
    ApiClass = create_api_class(class_name,(AbsRestApi, ),None)
    instance = ApiClass(*args)
    return instance

def get_rest_api_class(name,attributes=None):
    ApiClass = create_api_class(name,(AbsRestApi, ),attributes)
    return "halo_app.apis."+ApiClass.__name__

def create_api_class(name,bases,attributes=None):
    ApiClass = type(name+"Api", bases, {
        # constructor
        #"__init__": constructor,

        # views members
        #"string_attribute": "Geeks 4 geeks !",
        #"int_attribute": 1706256,
        "name" : name,

        # member functions
        #"func_arg": displayMethod,
        #"class_func": classMethod
    })
    return ApiClass

"""



##################################### test #########################
