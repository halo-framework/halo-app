from __future__ import print_function

import logging
from halo_app.classes import AbsBaseClass
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
class HaloResponse(AbsBaseClass):

    request = None
    payload = 'this is HaloResponse'
    code = 200
    headers = {}

    def __init__(self,halo_request, payload=None, code=None, headers=None):
        self.request = halo_request
        if payload:
            self.payload = payload
        if code:
            self.code = code
        if headers:
            self.headers = headers
