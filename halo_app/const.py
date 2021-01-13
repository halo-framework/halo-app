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
    event = "EVENT"
    command = "COMMAND"
    query = "QUERY"

ASYNC = "async"
SYNC = "sync"

class BusinessEventCategory(Enum):  # A subclass of Enum - if no category then implement handle method all the way
    EMPTY = "empty" # define a single api in code in method set_back_api
    API = "api" # define single api in config json
    SEQ = "seq" # define seq of api in config json
    SAGA = "saga" # define saga api in config json

