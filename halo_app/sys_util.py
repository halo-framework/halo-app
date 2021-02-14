from __future__ import print_function

import os
import logging
from halo_app.classes import AbsBaseClass
from halo_app.app.command import HaloCommand
from halo_app.app.event import AbsHaloEvent
from halo_app.const import LOC, OPType
from halo_app.app.context import HaloContext, InitCtxFactory
from halo_app.app.request import HaloEventRequest, HaloCommandRequest, AbsHaloRequest, HaloQueryRequest
from halo_app.view.query import AbsHaloQuery, HaloQuery
from .settingsx import settingsx
settings = settingsx()

logger = logging.getLogger(__name__)

BOUNDARY = None

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
    def instance_full_name(o):
        # o.__module__ + "." + o.__class__.__qualname__ is an example in
        # this context of H.L. Mencken's "neat, plausible, and wrong."
        # Python makes no guarantees as to whether the __module__ special
        # attribute is defined, so we take a more circumspect approach.
        # Alas, the module name is explicitly excluded from __qualname__
        # in Python 3.

        module = o.__class__.__module__
        if module is None or module == str.__class__.__module__:
            return o.__class__.__name__  # Avoid reporting __builtin__
        else:
            return module + '.' + o.__class__.__name__

    @staticmethod
    def create_command_request(halo_context: HaloContext, method_id: str, vars: dict,
                               security=None, roles=None) -> AbsHaloRequest:
        halo_command = HaloCommand(halo_context, method_id, vars)
        return HaloCommandRequest(halo_command, security, roles)

    @staticmethod
    def create_event_request(halo_event: AbsHaloEvent,
                               security=None, roles=None) -> AbsHaloRequest:
        return HaloEventRequest(halo_event, security, roles)

    @staticmethod
    def create_query_request(halo_query: HaloQuery,
                               security=None, roles=None) -> AbsHaloRequest:
        return HaloQueryRequest(halo_query, security, roles)

    @staticmethod
    def get_boundary():
        global BOUNDARY
        if BOUNDARY:
            return BOUNDARY
        from halo_app import bootstrap
        import importlib
        # bootstrap.COMMAND_HANDLERS["z0"] = A0.run_command_class
        for method_id in settings.HANDLER_MAP:
            clazz_type = settings.HANDLER_MAP[method_id]
            clazz = clazz_type["class"]
            type = clazz_type["type"]
            try:
                module_name, class_name = clazz.rsplit(".", 1)
                x = getattr(importlib.import_module(module_name), class_name)
                if type == OPType.COMMAND:  # command
                    bootstrap.COMMAND_HANDLERS[method_id] = x.run_command_class
                if type == OPType.QUERY:  # query
                    bootstrap.QUERY_HANDLERS[method_id] = x.run_query_class
                if type == OPType.EVENT:  # event
                    bootstrap.EVENT_HANDLERS[method_id] = x.run_event_class
            except Exception as e:
                logger.error("config for handler missing: "+str(clazz) +" - "+str(e))
                #@todo raise
                #raise e
        BOUNDARY = bootstrap.bootstrap()
        return BOUNDARY



