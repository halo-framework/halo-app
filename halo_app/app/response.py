from __future__ import print_function

import logging

from halo_app.app.context import HaloContext
from halo_app.app.exchange import AbsHaloExchange
from halo_app.app.request import AbsHaloRequest, HaloCommandRequest
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


    def __init__(self,halo_request:AbsHaloRequest):
        self.request = halo_request



class HaloCommandResponse(AbsHaloResponse):

    success = None

    def __init__(self,halo_request:AbsHaloRequest,success:bool=True):
        super(HaloCommandResponse,self).__init__(halo_request)
        self.success = success


class HaloQueryResponse(HaloCommandResponse):

    payload = None

    def __init__(self,halo_request:AbsHaloRequest,success:bool=True,payload=None):
        super(HaloQueryResponse, self).__init__(halo_request,success)
        if payload:
            self.payload = payload


class HaloResponseFactory(AbsBaseClass):

    def get_halo_response(self,halo_request:AbsHaloRequest,success:bool,payload=None)->AbsHaloResponse:
        if isinstance(halo_request, HaloCommandRequest) or issubclass(halo_request.__class__, HaloCommandRequest):
            return HaloCommandResponse(halo_request,success)
        else:
            return HaloQueryResponse(halo_request, success, payload)



