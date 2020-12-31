from __future__ import print_function

import os
from halo_app.classes import AbsBaseClass
from halo_app.domain.command import HaloCommand
from halo_app.const import LOC, OPType
from halo_app.app.context import HaloContext
from halo_app.app.request import HaloEventRequest, HaloCommandRequest, HaloRequest


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
    def create_request(halo_context: HaloContext, method_id: str, vars: dict, op_type: OPType = OPType.command,
                       security=None, roles=None) -> HaloRequest:
        halo_command = HaloCommand(halo_context, method_id, vars)
        return HaloCommandRequest(halo_command, security, roles)