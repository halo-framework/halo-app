from __future__ import print_function
# pylint: disable=attribute-defined-outside-init
from __future__ import annotations

from abc import ABCMeta,abstractmethod

from collections import OrderedDict

from halo_app.classes import AbsBaseClass
from halo_app.const import BusinessEventCategory


class AbsBusinessEvent(AbsBaseClass):
    __metaclass__ = ABCMeta

    EVENT_NAME = None
    EVENT_CATEGORY = None
    event_type = None

    @abstractmethod
    def __init__(self,event_name:str,event_category:BusinessEventCategory):
        self.EVENT_NAME = event_name
        self.EVENT_CATEGORY = event_category

    def get_business_event_name(self):
        return self.EVENT_NAME

    def get_business_category(self):
        return self.EVENT_CATEGORY

    def get_business_event_type(self):
        return self.event_type

class BusinessEvent(AbsBusinessEvent):
    pass

class ApiBusinessEvent(AbsBusinessEvent):

    __api = {}

    def __init__(self,event_name:str,event_category:BusinessEventCategory, dict):
        super(ApiBusinessEvent,self).__init__(event_name,event_category)
        self.event_type = BusinessEventCategory.API
        self.__api = OrderedDict(sorted(dict.items(), key=lambda t: t[0]))

    def get(self):
        return self.__api


class FoiBusinessEvent(AbsBusinessEvent):

    __foi = {} #first order interactions


    def __init__(self,event_name:str,event_category:BusinessEventCategory, dict):
        super(FoiBusinessEvent,self).__init__(event_name,event_category)
        self.event_type = BusinessEventCategory.SEQ
        self.__foi = OrderedDict(sorted(dict.items(), key=lambda t: t[0])) #SEQUANCE : api for target service

    def get(self, key):
        return self.__foi[key]

    def put(self, key, value):
        self.__foi[key] = value

    def keys(self):
        return self.__foi.keys()

class SagaBusinessEvent(AbsBusinessEvent):

    __saga = None

    def __init__(self,event_name:str,event_category:BusinessEventCategory, saga):
        super(SagaBusinessEvent,self).__init__(event_name,event_category)
        self.event_type = BusinessEventCategory.SAGA
        self.__saga = saga

    def get_saga(self):
        return self.__saga


