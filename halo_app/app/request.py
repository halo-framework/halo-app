from __future__ import print_function
import abc
import logging
# halo
from halo_app.classes import AbsBaseClass
from halo_app.exceptions import MissingHaloContextException
from halo_app.reflect import Reflect
from halo_app.security import HaloSecurity
from halo_app.app.context import HaloContext
from halo_app.settingsx import settingsx

logger = logging.getLogger(__name__)

settings = settingsx()

class HaloRequest(AbsBaseClass,abc.ABC):

    method_id = None
    vars = None
    context = None
    security = None
    sub_func = None

    @abc.abstractmethod
    def __init__(self,halo_context, method_id,vars,secure=False,method_roles=None):
        self.method_id = method_id
        self.vars = vars
        self.context = halo_context
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


class HaloCommandRequest(HaloRequest):
    command = None

    def __init__(self, halo_command, secure=False, method_roles=None):
        super(HaloCommandRequest,self).__init__(halo_command.context,halo_command.name,halo_command.vars,secure,method_roles)
        self.command = halo_command

class HaloQueryRequest(HaloRequest):
    query = None

    def __init__(self, halo_query,secure=False, method_roles=None):
        super(HaloQueryRequest,self).__init__(halo_query.context,halo_query.name,halo_query.vars,secure,method_roles)
        self.query = halo_query