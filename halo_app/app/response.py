from __future__ import print_function

import logging
import abc
from halo_app.app.context import HaloContext
from halo_app.app.exchange import AbsHaloExchange
from halo_app.app.request import AbsHaloRequest, HaloCommandRequest
from halo_app.classes import AbsBaseClass
from halo_app.entrypoints.client_type import ClientType
from halo_app.app.exceptions import MissingResponsetoClientTypeException

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

class AbsHaloResponse(AbsHaloExchange,abc.ABC):

    request = None

    @abc.abstractmethod
    def __init__(self,halo_request:AbsHaloRequest):
        self.request = halo_request



class HaloCommandResponse(AbsHaloResponse):

    success = None
    payload = None
    error = None

    def __init__(self,halo_request:AbsHaloRequest,success:bool=True,data=None):
        super(HaloCommandResponse,self).__init__(halo_request)
        self.success = success
        if success:
            self.payload = data
        else:
            self.error = data

class HaloQueryResponse(HaloCommandResponse):

    def __init__(self,halo_request:AbsHaloRequest,success:bool=True,payload=None):
        super(HaloQueryResponse, self).__init__(halo_request,success,payload)


class HaloResponseFactory(AbsBaseClass):

    def get_halo_response(self,halo_request:AbsHaloRequest,success:bool,data=None)->AbsHaloResponse:
        if isinstance(halo_request, HaloCommandRequest) or issubclass(halo_request.__class__, HaloCommandRequest):
            return HaloCommandResponse(halo_request,success,data)
        else:
            return HaloQueryResponse(halo_request, success, data)



