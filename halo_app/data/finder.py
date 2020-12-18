from halo_app.classes import AbsBaseClass
from halo_app.data.filters import Filter


class Dto(AbsBaseClass):
    pass

class AbsFinder(AbsBaseClass):
    def find(self,ids:dict,filters:[Filter]=None)->[Dto]:
        pass
