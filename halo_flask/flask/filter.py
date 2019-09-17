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

logger = logging.getLogger(__name__)

#https://hackernoon.com/analytics-for-restful-interfaces-579856dea9a9


class BaseEvent(AbsBaseClass):
    __metaclass__ = ABCMeta

    name = None
    time = None
    userId = None
    method = None
    country = None
    city = None
    region = None

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

class FilterChain(AbsBaseClass):

    list = None

    def __init__(self,list):
        self.list = list

    def do_filter(self, halo_request, halo_response):
        pass

#@WebFilter(filterName="RequestFilter", urlPatterns="/api/*")

class Filter(AbsBaseClass):
    __metaclass__ = ABCMeta

    config = None

    def __init__(self,config):
        self.config = config

class RequestFilter(Filter):

    def do_filter(self,halo_request,  halo_response):
        logger.debug("do_filter")
        #raise IOException, ServletException
        try:
            #catching all requests to api and logging
            #@todo fix filter config
            event = FilterEvent({})
            event.name = halo_request.request.path
            event.time = datetime.datetime.now()
            event.method = halo_request.request.method
            #event.userId = "user_" + (Random().nextInt(1000) + 1)
            event = self.augment_event_with_headers_and_data(event, halo_request,halo_response)
            inserted = store_util.put(event)
            if (not inserted):
                logger.debug("Event queue is full! inserted: " + str(inserted) + ", queue size: " + str(StoreUtil.eventQueue.qsize()))
        except StoreException as e:
            logger.debug("error:"+str(e))

    def augment_event_with_headers_and_data(self,event, halo_request,halo_response):
        #event.country = halo_request.request.headers["X-AppEngine-Country"]
        #event.city = halo_request.request.headers["X-AppEngine-City"]
        #event.region = halo_request.request.headers["X-AppEngine-Region"]
        return event


class StoreUtil(AbsBaseClass):
    eventQueue = queue.Queue()

    @staticmethod
    def put(event):
        print("StoreUtil:"+str(event.name))
        try:
            __class__.eventQueue.put(event)
            return True
        except Exception as e:
            raise StoreException(e)

store_util = StoreUtil()