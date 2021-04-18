from halo_app.domain.repository import AbsRepository
from halo_app.domain.model import Item

class SqlAlchemyRepository(AbsRepository):

    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, item):
        self.session.add(item)

    def _get(self, other):
        return self.session.query(Item).filter_by(other=other).first()

