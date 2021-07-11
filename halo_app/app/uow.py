# pylint: disable=attribute-defined-outside-init
from __future__ import annotations
import abc
from typing import Dict
from halo_app.classes import AbsBaseClass
from halo_app.domain.repository import AbsRepository


class AbsUnitOfWorkManager(abc.ABC):

    @abc.abstractmethod
    def start(self,method_id=None) -> AbsUnitOfWork:
        pass

#update one aggregate per aggregate
class AbsUnitOfWork(abc.ABC):

    repository:AbsRepository = None

    def __enter__(self) -> AbsUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError

    def collect_new_events(self):
        for item in self.repository.seen:
            while item.events:
                yield item.events.pop(0)

    @abc.abstractmethod
    def init_repository(self)->AbsRepository:
        raise NotImplementedError