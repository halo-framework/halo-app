from __future__ import print_function
import importlib
import jwt
import logging
import datetime
# halo
from halo_app.classes import AbsBaseClass
from halo_app.settingsx import settingsx

logger = logging.getLogger(__name__)

settings = settingsx()


class HaloContext(AbsBaseClass):

    method = "method"
    remote_addr = "remote_addr"
    host = "host"

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

    def __init__(self, headers=None):
        if headers:
            for key in self.items:
                flag = self.items[key]
                if flag in headers:
                    self.dict[key] = headers[flag]

    def get(self, key):
        if key in self.dict:
            return self.dict[key]
        return None

    def put(self, key, value):
        self.dict[key] = value

    def keys(self):
        return self.dict.keys()

    def size(self):
        return len(self.dict)





