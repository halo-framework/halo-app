from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Set

from halo_app.app.context import HaloContext
from halo_app.domain.entity import AbsHaloAggregateRoot
from halo_app.domain.event import AbsHaloDomainEvent


class Item(AbsHaloAggregateRoot):

    def __init__(self, id: str,  other: int = 0):
        super(Item, self).__init__(id)
        self.other = other


    def add(self, context, something: str) -> str:
        try:
            self.other += 1
            self.events.append(self.add_domain_event(context, something))
            return something
        except Exception:
            self.events.append(self.add_error_domain_event(context, something))
            return None



    def add_domain_event(self, context, something: str):
        class HaloDomainEvent(AbsHaloDomainEvent):
            def __init__(self, context: HaloContext, name: str,agg_root_id:str,something:str):
                super(HaloDomainEvent, self).__init__(context, name,agg_root_id)
                self.something = something

        return HaloDomainEvent(context, "good",self.agg_root_id,something)

    def add_error_domain_event(self, context, something: str):
        class HaloDomainEvent(AbsHaloDomainEvent):
            def __init__(self, context: HaloContext, name: str,agg_root_id:str,something:str):
                super(HaloDomainEvent, self).__init__(context, name,agg_root_id)
                self.something = something

        return HaloDomainEvent(context, "bad",self.agg_root_id,something)