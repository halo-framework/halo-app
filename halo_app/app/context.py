from __future__ import annotations
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

    remote_addr = "remote_addr"
    host = "ctx_host"
    client_type = "client_type"
    path = "ctx_path"

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
        ACCESS: "x-halo-access-token",
    }

    table:dict = {}

    def __init__(self, env:dict=None):
        if env:
            for key in self.items:
                flag = self.items[key]
                if flag in env:
                    self.table[key] = env[flag]

    def get(self, key):
        if key in self.table:
            return self.table[key]
        return None

    def put(self, key, value):
        self.table[key] = value

    def keys(self):
        return self.table.keys()

    def size(self):
        return len(self.table)

    def get_data(self):
        return self.table



class InitCtxFactory(AbsBaseClass):

    @staticmethod
    def get_initial_context(env:dict)->HaloContext:
        return HaloContext(env)


