from halo_app.classes import AbsBaseClass
from halo_app.domain.entity import AbsEntity


class AbsDomainService(AbsBaseClass):
    def validate(self,entity:AbsEntity)->bool:
        pass
