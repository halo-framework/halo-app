from __future__ import print_function

import importlib
import json
import logging
from abc import ABCMeta, abstractmethod

# DRF
from halo_app.infra.providers.exceptions import ProviderException
from halo_app.logs import log_json
from halo_app.infra.providers.providers import get_provider
from halo_app.classes import AbsBaseClass
from .app.utilx import Util
from .exceptions import AbsHaloException
from .reflect import Reflect
from .settingsx import settingsx

settings = settingsx()

logger = logging.getLogger(__name__)

class NoMessageException(AbsHaloException):
    pass


class NoTargetUrlException(AbsHaloException):
    pass

class AbsBaseEvent(AbsBaseClass):
    __metaclass__ = ABCMeta

    target_service = None
    target_service_name = None
    key_name = None
    key_val = None

    def get_loc_url(self):
        """

        :return:
        """
        if self.target_service in settings.LOC_TABLE:
            return settings.LOC_TABLE[self.target_service]
        raise NoTargetUrlException("not a local service")

    def send_event(self, messageDict, request=None, ctx=None):
        """

        :param messageDict:
        :param request:
        :param ctx:
        :return:
        """
        if messageDict:
            messageDict[self.key_name] = self.key_val
            messageDict[self.target_service + 'service_task_id'] = 'y'
            if request:
                ctx = Util.get_req_context(request)
            if ctx:
                messageDict.update(ctx)
        else:
            raise NoMessageException("not halo msg")
        if settings.SERVER_LOCAL:
            from multiprocessing.dummy import Pool
            import requests
            url = self.get_loc_url()
            pool = Pool(1)
            futures = []
            for x in range(1):
                futures.append(pool.apply_async(requests.post, [url], {'view': messageDict}))
            for future in futures:
                logger.debug("future:" + str(future.get()))
            return "sent event"
        else:
            try:
                service_name = self.target_service_name[settings.ENV_TYPE]
                logger.debug("send event to target_service:" + service_name, extra=log_json(ctx))
                ret = get_provider().send_event(ctx,messageDict,service_name)
            except ProviderException as e:
                logger.error("Unexpected Provider Error", extra=log_json(ctx, messageDict, e))
            else:
                logger.debug("send_event to service " + self.target_service + " ret: " + str(ret),
                             extra=log_json(ctx, messageDict))
        return ret


class AbsMainHandler(AbsBaseClass):
    __metaclass__ = ABCMeta

    keys = []
    vals = {}
    classes = {}

    def get_event(self, event, context):
        logger.debug('get_event : ' + str(event))
        self.process_event(event, context)

    def process_event(self, event, context):
        """

        :param event:
        :param context:
        """
        for key in self.keys:
            if key in event:
                val = self.vals[key]
                if val == event[key]:
                    class_name = self.classes[key]
                    #module = importlib.import_module(settings.MIXIN_HANDLER)
                    #logger.debug('module : ' + str(module))
                    #class_ = getattr(module, class_name)
                    #instance = class_()
                    instance = Reflect.do_instantiate(settings.MIXIN_HANDLER,class_name, None)
                    instance.do_event(event, context)


class AbsBaseHandler(AbsBaseClass):
    __metaclass__ = ABCMeta

    key_name = None
    key_val = None

    def do_event(self, event, context):
        """

        :param event:
        :param context:
        """
        req_context = Util.get_correlation_from_event(event)
        logger.debug(' get_event : ' + str(event), extra=log_json(req_context))
        self.process_event(event, context)

    @abstractmethod
    def process_event(self, event, context):
        pass
