from __future__ import print_function

import logging
from halo_flask.classes import AbsBaseClass
logger = logging.getLogger(__name__)


class HaloRequest(AbsBaseClass):

    request = None
    sub_func = None

    def __init__(self, request, sub_func=None):
        if request:
            self.request = request
            self.sub_func = sub_func
