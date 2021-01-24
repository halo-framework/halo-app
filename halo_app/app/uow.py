# pylint: disable=attribute-defined-outside-init
from __future__ import annotations
import abc


from halo_app.domain.repository import AbsRepository


class AbsUnitOfWork(abc.ABC):

    items: AbsRepository = None

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
        for item in self.items.seen:
            while item.events:
                yield item.events.pop(0)


