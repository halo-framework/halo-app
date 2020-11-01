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


    dict = {}

    def __init__(self, dict):
        self.dict = dict

    def get(self, key):
        return self.dict[key]

    def put(self, key, value):
        self.dict[key] = value

    def keys(self):
        return self.dict.keys()

    def serialize(self):
        d = {'name':self.name,'time':str(self.time),'method':self.method,'remote_addr':self.remote_addr,'host':self.host}
        if len(self.dict) > 0:
            d.update(self.dict)
        return str(d)


class FilterEvent(BaseEvent):
    pass

class Filter(AbsBaseClass):
    __metaclass__ = ABCMeta

    def do_filter(self,halo_request,  halo_response):
        pass

    def augment_event_with_headers_and_data(self, event, halo_request, halo_response):
        pass

class RequestFilter(Filter):

    def do_filter(self,halo_request,  halo_response):
        logger.debug("do_filter")
        try:
            #catching all requests to api and logging them for analytics
            event = FilterEvent({})
            event.name = halo_request.request.path
            event.time = datetime.datetime.now()
            event.method = halo_request.request.method
            event.remote_addr = halo_request.request.remote_addr
            event.host = halo_request.request.host
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
            if HaloContext.items[key] in halo_request.request.headers:
                event.put(HaloContext.items[key],halo_request.request.headers[HaloContext.items[key]])
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
