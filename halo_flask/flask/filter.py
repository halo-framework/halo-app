from __future__ import print_function

# python
import datetime
import logging
import os
import traceback
from abc import ABCMeta
import queue
import time
import importlib
import threading

from flask import current_app as app
from halo_flask.exceptions import StoreException,StoreClearException
from halo_flask.classes import AbsBaseClass
from halo_flask.request import HaloContext
from halo_flask.settingsx import settingsx
from halo_flask.executor import get_executor
from ..exceptions import *
from ..reflect import Reflect

logger = logging.getLogger(__name__)

#https://hackernoon.com/analytics-for-restful-interfaces-579856dea9a9

settings = settingsx()

sem = threading.Semaphore()

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
            if store_util.clearing():
                inserted = store_util.put(event)
                if (not inserted):
                    logger.error("Event queue is full! inserted: " + str(inserted) + ", queue size: " + str(StoreUtil.event_queue.qsize()))
            else:
                logger.error("Event queue is not clearing! , queue size: " + str(
                    StoreUtil.event_queue.qsize()))
        except StoreException as e:
            logger.debug("error:"+str(e))

    def augment_event_with_headers_and_data(self,event, halo_request,halo_response):
        # context data
        for key in HaloContext.items.keys():
            if HaloContext.items[key] in halo_request.request.headers:
                event.put(HaloContext.items[key],halo_request.request.headers[HaloContext.items[key]])
        return event

class RequestFilterClear(AbsBaseClass):

    def __init__(self, events):
        self.events = events

    def run(self):
        for event in self.events:
            logger.debug("insert_events_to_repository " + str(event.serialize()))

# @todo monitor the job
def exec_callback(future):
    if future:
        logger.info("StoreUtil: executor finished - " + str(future.result()))
        if future.exception():
            logger.info("StoreUtil: executor exception - " + str(future.exception()))
    StoreUtil.set_flag()

#@todo consider adding api call to start executor
#@app.route('/start-task')
#def start_task():
    #store_util.clearing()
    #return jsonify({'result':'success'})

#thread safe including the event queue and set_flag
class StoreUtil(AbsBaseClass):
    event_queue = queue.Queue()
    config = None
    flag = False

    def __init__(self, config):
        self.config = config

    @staticmethod
    def clearing():
        if not __class__.flag:
            executor = get_executor()
            if executor:
                executor.add_default_done_callback(exec_callback)
                executor.submit(__class__.start_queue_listener)
                __class__.flag = True
        return __class__.flag

    @staticmethod
    def set_flag():
        sem.acquire()
        __class__.flag = False
        sem.release()

    @staticmethod
    def put(event):
        logger.debug("StoreUtil:"+str(event.name))
        try:
            __class__.event_queue.put(event)
            return True
        except Exception as e:
            raise StoreException(e)

    @staticmethod
    def insert_events_to_repository(events):
        if settings.REQUEST_FILTER_CLEAR_CLASS:
            clazz = Reflect.instantiate(settings.REQUEST_FILTER_CLEAR_CLASS,RequestFilterClear,events)
        else:
            clazz = RequestFilterClear(events)
        clazz.run()

    @staticmethod
    def start_queue_listener():
        logger.debug("start_queue_listener")
        try:
            while (True):
                size = __class__.event_queue.qsize()
                logger.debug("while start_queue_listener "+str(size))
                numberOfIngested = 0;
                if size > 0:
                    events = []
                    maxer = min([settings.EVENTS_INGESTED,size])
                    for i in range(0,maxer):
                        event =  __class__.event_queue.get()
                        events.append(event)
                    __class__.insert_events_to_repository(events)
                    numberOfIngested = __class__.event_queue.qsize()
                if numberOfIngested < settings.EVENTS_INGESTED:
                    time.sleep(settings.EVENTS_INGESTED_SLEEP);
        except Exception as e:
            logger.debug("Event queue loop broken! , queue size: " + str(
                StoreUtil.event_queue.qsize()))
            raise StoreClearException(e)


store_util = StoreUtil(settings.REQUEST_FILTER_CONFIG)
