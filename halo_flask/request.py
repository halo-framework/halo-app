from __future__ import print_function
import importlib
import logging
from halo_flask.classes import AbsBaseClass
from halo_flask.exceptions import HaloException,MissingHaloContextException
from .settingsx import settingsx

logger = logging.getLogger(__name__)

settings = settingsx()


class HaloContext(AbsBaseClass):

    CORRELATION = "CORRELATION"
    USER_AGENT = "USER AGENT"
    REQUEST = "REQUEST"
    DEBUG_LOG = "DEBUG LOG"
    API_KEY = "API KEY"
    SESSION = "SESSION"
    ACCESS = "ACCESS"

    items = {
        CORRELATION:"x-halo-correlation-id",
        USER_AGENT: "x-halo-user-agent",
        REQUEST: "x-halo-request-id",
        DEBUG_LOG: "x-halo-debug-log-enabled",
        API_KEY: "x-halo-api-key",
        SESSION: "x-halo-session-id",
        ACCESS: "x-halo-access-token"
    }

    dict = {}

    def __init__(self, request):
        for key in self.items:
            flag = self.items[key]
            if flag in request.headers:
                self.dict[key] = request.headers[flag]

    def get(self, key):
        return self.dict[key]

    def put(self, key, value):
        self.dict[key] = value

    def keys(self):
        return self.dict.keys()

    def size(self):
        return len(self.dict)

class HaloRequest(AbsBaseClass):

    request = None
    sub_func = None
    context = None

    def __init__(self, request, sub_func=None):
        self.request = request
        self.sub_func = sub_func
        self.context = self.init_ctx(request)
        for i in settings.HALO_CONTEXT_LIST:
            if i not in self.context.keys():
                raise MissingHaloContextException(i)

    def init_ctx(self, request):
        if settings.HALO_CONTEXT_CLASS:
            k = settings.HALO_CONTEXT_CLASS.rfind(".")
            module_name = settings.HALO_CONTEXT_CLASS[:k]
            class_name = settings.HALO_CONTEXT_CLASS[k+1:]
            module = importlib.import_module(module_name)
            class_ = getattr(module, class_name)
            if not issubclass(class_, HaloContext):
                raise HaloException("HALO CONTEXT CLASS error:"+settings.HALO_CONTEXT_CLASS)
            instance = class_(request)
        else:
            instance = HaloContext(request)
        return instance