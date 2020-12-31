from halo_app.classes import AbsBaseClass
from halo_app.domain.entity import AbsHaloEntity


class AbsDomainService(AbsBaseClass):
    def validate(self,entity:AbsHaloEntity)->bool:
        pass
