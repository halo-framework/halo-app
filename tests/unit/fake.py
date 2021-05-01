from __future__ import annotations
from collections import defaultdict
from datetime import date
from typing import Dict, List
import pytest

from halo_app.app.bus import Bus
from halo_app.app.event import AbsHaloEvent
from halo_app.app.request import AbsHaloRequest, HaloCommandRequest
from halo_app.app.response import HaloResponseFactory, AbsHaloResponse, HaloCommandResponse
from halo_app.classes import AbsBaseClass
from halo_app.domain.repository import AbsRepository
from halo_app.app.uow import AbsUnitOfWork
from halo_app.entrypoints import client_util
from halo_app.entrypoints.client_type import ClientType
from halo_app.entrypoints.event_consumer import AbsConsumer
from halo_app.infra.event_publisher import AbsPublisher
from halo_app.infra.notifications import AbstractNotifications


class FakeRepository(AbsRepository):

    def __init__(self, products):
        super().__init__()
        self._products = set(products)

    def _add(self, product):
        self._products.add(product)

    def _get(self, id):
        return next((p for p in self._products if p.id == id), None)




class FakeUnitOfWork(AbsUnitOfWork):

    def __init__(self):
        self.items = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass


    def __call__(self, repository_type):
        return self.items


class FakePublisher(AbsPublisher):
    def __init__(self):
        super(FakePublisher, self).__init__()
        class Publisher():
            def publish(self,channel, json):
                pass
        self.publisher = Publisher()


class FakeConsumer(AbsConsumer):
    def __init__(self):
        super(FakeConsumer, self).__init__()


class FakeBus(Bus):
    def fake_process(self,event):
        super(FakeBus,self)._process_event(event)



class FakeNotifications(AbstractNotifications):

    def __init__(self):
        self.sent = defaultdict(list)  # type: Dict[str, List[str]]

    def send(self, destination, message):
        self.sent[destination].append(message)


class XClientType(ClientType):
    tester = 'TESTER'

class XHaloResponseFactory(HaloResponseFactory):

    def get_halo_response(self, halo_request: AbsHaloRequest, success: bool, payload) -> AbsHaloResponse:
        class TesterHaloResponse(HaloCommandResponse):
            pass
        if isinstance(halo_request, HaloCommandRequest) or issubclass(halo_request.__class__, HaloCommandRequest):
            return TesterHaloResponse(halo_request, success,payload)
        return super(XHaloResponseFactory,self).get_halo_response(halo_request,success, payload)
