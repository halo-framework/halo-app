from __future__ import print_function

import logging
from halo_flask.classes import AbsBaseClass
logger = logging.getLogger(__name__)


class HaloRequest(AbsBaseClass):

    request = None
    behavior_qualifier = None

    def __init__(self, request):
        if request:
            self.request = request
            self.behavior_qualifier = self.set_behavior_qualifier(request)

    def set_behavior_qualifier(self,request):
        return None