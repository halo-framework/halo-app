from __future__ import print_function
import importlib
import logging
import datetime
# halo
from halo_flask.classes import AbsBaseClass
from halo_flask.exceptions import HaloException,MissingHaloContextException
from halo_flask.reflect import Reflect
from halo_flask.security import HaloSecurity
from halo_flask.context import HaloContext
from halo_flask.flask.utilx import Util
from halo_flask.settingsx import settingsx

logger = logging.getLogger(__name__)

settings = settingsx()

class HaloRequest(AbsBaseClass):

    request = None
    sub_func = None
    context = None
    security = None

    def __init__(self, request, sub_func=None,secure=False,method_roles=None):
        self.request = request
        self.sub_func = sub_func
        self.context = self.init_ctx(request)
        for i in settings.HALO_CONTEXT_LIST:
            item = HaloContext.items[i]
            if item not in self.context.keys():
                raise MissingHaloContextException(str(item))
        if settings.SECURITY_FLAG or secure:
            if settings.HALO_SECURITY_CLASS:
                self.security = Reflect.instantiate(settings.HALO_SECURITY_CLASS, HaloSecurity, request)
            else:
                self.security = HaloSecurity(request)
            self.security.validate_method(method_roles)

    def init_ctx(self, request):
        context = Util.get_halo_context(request)
        if settings.HALO_CONTEXT_CLASS:
            context = Reflect.instantiate(settings.HALO_CONTEXT_CLASS,HaloContext,request)
        return context




