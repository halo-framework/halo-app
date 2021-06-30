import abc
from halo_app.domain.entity import AbsHaloAggregateRoot
from halo_app.domain.repository import AbsRepository

class SqlAlchemyRepository(AbsRepository):

    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, item: AbsHaloAggregateRoot):
        self.session.add(item)

    def _get(self, aggregate_id):
        #return self.session.query(self.aggregate_type).filter_by(id=aggregate_id).first()
        q = self.session.query(self.aggregate_type)
        return q.filter_by(id=aggregate_id).first()

