from flask import jsonify

from halo_app.app.response import AbsHaloResponse
from halo_app.app.dto import AbsHaloDto as Dto

class HaloViewResponse(AbsHaloResponse):
    def __init__(self, data:[Dto], code=None, headers=None):
        super(HaloViewResponse,self).__init__(None,None,code,headers)
        if data:
            self.payload = self.data_to_payload(data)

    def data_to_payload(self,data):
        return jsonify(data)