from halo_app.classes import AbsBaseClass
from halo_app.domain.entity import BaseAggregateRoot


class AbsRepository(AbsBaseClass):
    def persist(self,entity:BaseAggregateRoot):
        pass

    def save(self,entity:BaseAggregateRoot)->BaseAggregateRoot:
        pass

    def load(self,entity_id)->BaseAggregateRoot:
        pass
