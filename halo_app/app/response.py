from __future__ import print_function

import logging

from halo_app.app.context import HaloContext
from halo_app.app.exchange import AbsHaloExchange
from halo_app.app.request import AbsHaloRequest
from halo_app.classes import AbsBaseClass
from halo_app.entrypoints.client_type import ClientType
from halo_app.exceptions import MissingResponsetoClientTypeError

logger = logging.getLogger(__name__)

"""
{
    "statusCode": 200,
    "headers": {
      "Content-Type": "application/json"
    },
    "isBase64Encoded": false,
    "multiValueHeaders": { 
      "X-Custom-Header": ["My value", "My other value"],
    },
    "body": "{\n  \"TotalCodeSize\": 104330022,\n  \"FunctionCount\": 26\n}"
  }
"""

class AbsHaloResponse(AbsHaloExchange):

    request = None
    payload = None
    success = None

    def __init__(self,halo_request,success=True, payload=None):
        self.request = halo_request
        self.success = success
        if payload:
            self.payload = payload


class ApiHaloResponse(AbsHaloResponse):

    code = 200
    headers = {}

    def __init__(self,halo_request:AbsHaloRequest,success:bool=True, payload=None, code=None, headers=None):
        super(ApiHaloResponse,self).__init__(halo_request,success, payload)
        if code:
            self.code = code
        if headers:
            self.headers = headers

class CliHaloResponse(AbsHaloResponse):

    env = {}

    def __init__(self,halo_request:AbsHaloRequest,success:bool=True, payload=None, env=None):
        super(CliHaloResponse,self).__init__(halo_request,success, payload)
        if env:
            self.env = env


class HaloResponseFactory(AbsBaseClass):

    def get_halo_response(self,halo_request:AbsHaloRequest,success:bool,payload,env:dict=None)->AbsHaloResponse:
        if halo_request.context.get(HaloContext.client_type) == ClientType.api:
            return ApiHaloResponse(halo_request,success, payload,env)
        if halo_request.context.get(HaloContext.client_type) == ClientType.cli:
            return CliHaloResponse(halo_request, success, payload)
        else:
            raise MissingResponsetoClientTypeError(halo_request.context.get(HaloContext.client_type))


