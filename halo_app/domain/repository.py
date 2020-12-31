# pylint: disable=attribute-defined-outside-init
from __future__ import annotations

from halo_app.classes import AbsBaseClass
from halo_app.domain.entity import AbsHaloAggregateRoot
from halo_app.domain.model import Item

class AbsRepository(AbsBaseClass):

    def __init__(self):
        self.seen = set()

    def persist(self,entity:AbsHaloAggregateRoot):
        pass

    def save(self,entity:AbsHaloAggregateRoot)->AbsHaloAggregateRoot:
        pass

    def load(self,entity_id)->AbsHaloAggregateRoot:
        pass


