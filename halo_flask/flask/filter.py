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

    def do_filter(self,halo_request,  halo_response,  chain=None):
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
            event = self.augment_event_with_headers(event, halo_request)
            inserted = store_util.put(event)
            if (not inserted):
                logger.debug("Event queue is full! inserted: " + str(inserted) + ", queue size: " + str(StoreUtil.eventQueue.qsize()))
        except StoreException as e:
            logger.debug("do_filter")
        if chain:
            chain.do_filter(halo_request, halo_response)


    def augment_event_with_headers(self,event, halo_request):
        #event.country = halo_request.request.headers["X-AppEngine-Country"]
        #event.city = halo_request.request.headers["X-AppEngine-City"]
        #event.region = halo_request.request.headers["X-AppEngine-Region"]
        return event


class StoreUtil(AbsBaseClass):
    eventQueue = queue.Queue()

    @staticmethod
    def put(event):
        logger.info("StoreUtil:"+str(event))
        __class__.eventQueue.put(event)

store_util = StoreUtil()