# pylint: disable=attribute-defined-outside-init
from __future__ import annotations
from abc import abstractmethod
from halo_app.classes import AbsBaseClass
from halo_app.domain.entity import AbsHaloAggregateRoot
from halo_app.domain.model import Item

#Define one repository per aggregate
class AbsRepository(AbsBaseClass):

    aggregate_type = None

    def __init__(self,):
        self.seen = set()


    @abstractmethod
    def persist(self,entity:AbsHaloAggregateRoot):
        pass

    @abstractmethod
    def save(self,entity:AbsHaloAggregateRoot)->AbsHaloAggregateRoot:
        pass

    @abstractmethod
    def load(self,entity_id)->AbsHaloAggregateRoot:
        pass


