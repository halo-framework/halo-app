from __future__ import print_function

# python
import datetime
import logging
import os
import traceback
from abc import ABCMeta
import queue
import time

from halo_app.exceptions import StoreException,StoreClearException
from halo_app.classes import AbsBaseClass
from halo_app.request import HaloContext
from halo_app.settingsx import settingsx
from halo_app.reflect import Reflect

logger = logging.getLogger(__name__)

#https://hackernoon.com/analytics-for-restful-interfaces-579856dea9a9

settings = settingsx()

class BaseEvent(AbsBaseClass):
    __metaclass__ = ABCMeta

    name = None
    time = None
    method = None
    remote_addr = None
    host = None


    table = {}

    def __init__(self, table):
        self.table = table

    def get(self, key):
        return self.table[key]

    def put(self, key, value):
        self.table[key] = value

    def keys(self):
        return self.table.keys()

    def serialize(self):
        d = {'name':self.name,'time':str(self.time),'method':self.method,'remote_addr':self.remote_addr,'host':self.host}
        if len(self.table) > 0:
            d.update(self.table)
        return str(d)


class FilterEvent(BaseEvent):
    pass

class AbsFilter(AbsBaseClass):
    __metaclass__ = ABCMeta

    def do_filter(self,halo_request,  halo_response):
        pass

    def augment_event_with_headers_and_data(self, event, halo_request, halo_response):
        pass

class RequestFilter(AbsFilter):

    def do_filter(self,halo_request,  halo_response):
        logger.debug("do_filter")
        try:
            #catching all requests to api and logging them for analytics
            event = FilterEvent({})
            event.name = halo_request.method_id
            event.time = datetime.datetime.now()
            event.method = halo_request.context.get(HaloContext.method)
            event.remote_addr = halo_request.context.get(HaloContext.remote_addr)
            event.host = halo_request.context.get(HaloContext.host)
            if halo_request.sub_func:
                event.put("sub_func", halo_request.sub_func)
            event = self.augment_event_with_headers_and_data(event, halo_request,halo_response)
            if store_util:
                inserted = store_util.put(event)
                if (not inserted):
                    logger.error("Event queue insert failed: " + str(inserted))
            else:
                logger.error("Event queue is not active!")
        except StoreException as e:
            logger.info("event filter error:"+str(e))

    def augment_event_with_headers_and_data(self,event, halo_request,halo_response):
        # context data
        for key in HaloContext.items.keys():
            if HaloContext.items[key] in halo_request.context.keys():
                event.put(HaloContext.items[key],halo_request.context.get(HaloContext.items[key]))
        return event

class RequestFilterClear(AbsBaseClass):

    def __init__(self):
        pass

    def run(self,event):
        logger.debug("insert_events_to_repository " + str(event.serialize()))

#thread safe including the event queue and set_flag
class StoreUtil(AbsBaseClass):
    config = None
    cleaner = None

    def __init__(self, config):
        self.config = config

    def put(self,event):
        logger.debug("StoreUtil:"+str(event.name))
        try:
            if not self.cleaner:
                self.cleaner = self.insert_events_to_repository_class()
            self.cleaner.run(event)
            return True
        except Exception as e:
            raise StoreException("failed to clear events",e)

    def insert_events_to_repository_class(self):
        if settings.REQUEST_FILTER_CLEAR_CLASS:
            clazz = Reflect.instantiate(settings.REQUEST_FILTER_CLEAR_CLASS,RequestFilterClear)
        else:
            clazz = RequestFilterClear()
        return clazz


store_util = StoreUtil(settings.REQUEST_FILTER_CONFIG)
