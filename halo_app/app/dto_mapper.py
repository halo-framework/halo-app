import abc
from mapper.object_mapper import ObjectMapper

from halo_app.app.dto import AbsHaloDto
from halo_app.classes import AbsBaseClass


class AbsHaloDtoMapper(AbsBaseClass,abc.ABC):
    mapper = None
    def __init__(self):
        self.mapper = ObjectMapper()

    @abc.abstractmethod
    def map_to_dto(self,object,dto:AbsHaloDto):
        pass

    @abc.abstractmethod
    def map_from_dto(self,dto:AbsHaloDto,object):
        pass