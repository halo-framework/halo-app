from __future__ import print_function
import importlib
import logging
import datetime
# halo
from halo_app.classes import AbsBaseClass
from halo_app.exceptions import HaloException,MissingHaloContextException
from halo_app.reflect import Reflect
from halo_app.security import HaloSecurity
from halo_app.context import HaloContext
from halo_app.app.utilx import Util
from halo_app.settingsx import settingsx

logger = logging.getLogger(__name__)

settings = settingsx()

class HaloRequest(AbsBaseClass):

    request = None
    sub_func = None
    context = None
    security = None

    def __init__(self, sub_func=None,secure=False,method_roles=None,context=None):
        self.sub_func = sub_func
        self.context = context
        for i in settings.HALO_CONTEXT_LIST:
            item = HaloContext.items[i]
            if item not in self.context.keys():
                raise MissingHaloContextException(str(item))
        if settings.SECURITY_FLAG or secure:
            if settings.HALO_SECURITY_CLASS:
                self.security = Reflect.instantiate(settings.HALO_SECURITY_CLASS, HaloSecurity)
            else:
                self.security = HaloSecurity()
            self.security.validate_method(method_roles)

    def init_ctx(self):
        context = Util.get_halo_context()
        if settings.HALO_CONTEXT_CLASS:
            context = Reflect.instantiate(settings.HALO_CONTEXT_CLASS,HaloContext)
        return context



