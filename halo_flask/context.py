from __future__ import print_function

import logging
from halo_flask.classes import AbsBaseClass
logger = logging.getLogger(__name__)
from .settingsx import settingsx

settings = settingsx()

class HaloContext(AbsBaseClass):

    CORRELATION = "CORRELATION"
    USER_AGENT = "USER AGENT"
    REQUEST = "REQUEST"
    DEBUG_LOG = "DEBUG LOG"
    API_KEY = "API KEY"

    items = {
        CORRELATION:"x-correlation-id",
        USER_AGENT: "x-user-agent",
        REQUEST: "x-request-id",
        DEBUG_LOG: "x-debug-log-enabled",
        API_KEY: "x-api-key"
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