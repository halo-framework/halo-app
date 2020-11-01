from __future__ import print_function

import os
from halo_app.classes import AbsBaseClass
from halo_app.const import LOC

class SysUtil(AbsBaseClass):
    @staticmethod
    def get_stage():
        """

        :return:
        """
        if 'HALO_STAGE' in os.environ:
            return os.environ['HALO_STAGE']
        return LOC