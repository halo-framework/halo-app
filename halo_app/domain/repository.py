# pylint: disable=attribute-defined-outside-init
from __future__ import annotations
from abc import ABC,abstractmethod
from typing import Set

from halo_app.classes import AbsBaseClass
from halo_app.domain.entity import AbsHaloAggregateRoot

#Define one repository per aggregate
class AbsRepository(AbsBaseClass,ABC):

    aggregate_type:type = None

    def __init__(self):
        self.seen:set = set()
        aggregate_type = self.get_type()

    def add(self, item: AbsHaloAggregateRoot):
        self._add(item)
        self.seen.add(item)

    def get(self, aggregate_id) -> AbsHaloAggregateRoot:
        item = self._get(aggregate_id)
        if item:
            self.seen.add(item)
        return item

    @abstractmethod
    def _add(self, item: AbsHaloAggregateRoot):
        raise NotImplementedError

    @abstractmethod
    def _get(self, aggregate_id) -> AbsHaloAggregateRoot:
        raise NotImplementedError

    @abstractmethod
    def get_type(self)->type:
        raise NotImplementedError
