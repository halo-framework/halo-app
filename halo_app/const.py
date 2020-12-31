from __future__ import print_function

from enum import Enum


LOC = 'loc'
DEV = 'dev'
TST = 'tst'
PRD = 'prd'


class HTTPChoice(Enum):  # A subclass of Enum
    get = "GET"
    post = "POST"
    put = "PUT"
    delete = "DELETE"
    patch = "PATCH"


class SYSTEMChoice(Enum):  # A subclass of Enum
    dbaccess = "DBACCESS"
    server = "SERVER"
    api = "API"
    saga = "SAGA"
    cache = "CACHE"

class LOGChoice(Enum):  # A subclass of Enum
    performance_data = "performance_data"
    type = "type"
    milliseconds = "milliseconds"
    error_performance_data = "error_performance_data"
    function = "function"
    saga = "saga"
    url = "url"

class OPType(Enum):  # A subclass of Enum
    query = "QUERY"
    command = "COMMAND"

ASYNC = "async"