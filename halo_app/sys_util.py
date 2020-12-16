from __future__ import print_function

import os
from halo_app.classes import AbsBaseClass
from halo_app.command import HaloQuery, HaloCommand
from halo_app.const import LOC, OPType
from halo_app.context import HaloContext
from halo_app.request import HaloQueryRequest, HaloCommandRequest, HaloRequest


class SysUtil(AbsBaseClass):
    @staticmethod
    def get_stage():
        """

        :return:
        """
        if 'HALO_STAGE' in os.environ:
            return os.environ['HALO_STAGE']
        return LOC

    @staticmethod
    def create_request(halo_context: HaloContext, method_id: str, args: dict, op_type: OPType = OPType.command,
                       security=None, roles=None) -> HaloRequest:
        if op_type == OPType.query:
            halo_query = HaloQuery(halo_context, method_id, args)
            return HaloQueryRequest(halo_query, security, roles)
        halo_command = HaloCommand(halo_context, method_id, args)
        return HaloCommandRequest(halo_command, security, roles)