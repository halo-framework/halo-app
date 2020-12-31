from __future__ import print_function
# pylint: disable=attribute-defined-outside-init
from __future__ import annotations

from abc import ABCMeta

from collections import OrderedDict

SEQ = "seq"
SAGA = "saga"

class BusinessEvent:
    __metaclass__ = ABCMeta

    EVENT_NAME = None
    EVENT_CATEGORY = None
    event_type = None

    def __init__(self,event_name,event_category):
        self.EVENT_NAME = event_name
        self.EVENT_CATEGORY = event_category

    def get_business_event_name(self):
        return self.EVENT_NAME

    def get_business_category(self):
        return self.EVENT_CATEGORY

    def get_business_event_type(self):
        return self.event_type


class FoiBusinessEvent(BusinessEvent):

    foi = {} #first order interactions


    def __init__(self,event_name,event_category, dict):
        self.EVENT_NAME = event_name
        self.EVENT_CATEGORY = event_category
        self.event_type = SEQ
        self.foi = OrderedDict(sorted(dict.items(), key=lambda t: t[0])) #SEQUANCE : api for target service domain/service operation-apiobj

    def get(self, key):
        return self.foi[key]

    def put(self, key, value):
        self.foi[key] = value

    def keys(self):
        return self.foi.keys()

class SagaBusinessEvent(BusinessEvent):

    saga = None

    def __init__(self,event_name,event_category, saga):
        self.EVENT_NAME = event_name
        self.EVENT_CATEGORY = event_category
        self.event_type = SAGA
        self.saga = saga

    def get_saga(self, key):
        return self.saga