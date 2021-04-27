from __future__ import annotations
import abc
import logging
# halo
from halo_app.app.exchange import AbsHaloExchange
from halo_app.app.command import HaloCommand
from halo_app.classes import AbsBaseClass
from halo_app.app.event import AbsHaloEvent
from halo_app.app.exceptions import MissingHaloContextException
from halo_app.reflect import Reflect
from halo_app.security import HaloSecurity
from halo_app.app.context import HaloContext
from halo_app.settingsx import settingsx
from halo_app.app.query import HaloQuery

logger = logging.getLogger(__name__)

settings = settingsx()

class AbsHaloRequest(AbsHaloExchange,abc.ABC):

    method_id = None
    context = None
    security = None

    @abc.abstractmethod
    def __init__(self,halo_context:HaloContext, method_id:str,vars,secure=False,method_roles=None):
        self.method_id = method_id
        self.context = halo_context
        for i in settings.HALO_CONTEXT_LIST:
            if i not in HaloContext.items:
                raise MissingHaloContextException(str(i))
            if i not in self.context.keys():
                raise MissingHaloContextException(str(i))
        if settings.SECURITY_FLAG or secure:
            if settings.HALO_SECURITY_CLASS:
                self.security = Reflect.instantiate(settings.HALO_SECURITY_CLASS, HaloSecurity)
            else:
                self.security = HaloSecurity()
            self.security.validate_method(method_roles)


class HaloCommandRequest(AbsHaloRequest):
    command = None
    usecase_id = None

    def __init__(self,halo_context:HaloContext, halo_command:HaloCommand, secure=False, method_roles=None):
        super(HaloCommandRequest,self).__init__(halo_context,halo_command.name,secure,method_roles)
        self.command = halo_command

class HaloEventRequest(AbsHaloRequest):
    event = None

    def __init__(self,halo_context:HaloContext, halo_event:AbsHaloEvent,secure=False, method_roles=None):
        super(HaloEventRequest, self).__init__(halo_context, halo_event.name, secure, method_roles)
        self.event = halo_event

class HaloQueryRequest(AbsHaloRequest):
    query = None

    def __init__(self,halo_context:HaloContext, halo_query:HaloQuery,secure=False, method_roles=None):
        super(HaloQueryRequest, self).__init__(halo_context, halo_query.name, secure, method_roles)
        self.query = halo_query


