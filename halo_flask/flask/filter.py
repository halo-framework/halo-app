from __future__ import print_function

# python
import datetime
import logging
import os
import traceback
from abc import ABCMeta
import queue

from halo_flask.exceptions import StoreException

from halo_flask.classes import AbsBaseClass
from halo_flask.settingsx import settingsx

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
            event = self.augment_event_with_headers_and_data(event, halo_request,halo_response)
            inserted = store_util.put(event)
            if (not inserted):
                logger.debug("Event queue is full! inserted: " + str(inserted) + ", queue size: " + str(StoreUtil.eventQueue.qsize()))
        except StoreException as e:
            logger.debug("error:"+str(e))

    def augment_event_with_headers_and_data(self,event, halo_request,halo_response):
        if "x-correlation-id" in halo_request.request.headers:
            event.put("x-correlation-id",halo_request.request.headers["x-correlation-id"])
        if halo_request.sub_func:
            event.put("sub_func",halo_request.sub_func)
        return event


class StoreUtil(AbsBaseClass):
    eventQueue = queue.Queue()
    config = None

    def __init__(self, config):
        self.config = config

    @staticmethod
    def put(event):
        print("StoreUtil:"+str(event.name))
        try:
            __class__.eventQueue.put(event)
            return True
        except Exception as e:
            raise StoreException(e)

store_util = StoreUtil(settings.REQUEST_FILTER_CONFIG)