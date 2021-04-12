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

class DtoMapper(AbsHaloDtoMapper):
    def __init__(self):
        super(DtoMapper, self).__init__()

    def map_from_dto(self,dto:AbsHaloDto,object_class_type):
        super.mapper.create_map(dto.__class__, object_class_type)
        object = super.mapper.map(dto, object_class_type)
        return object

    def map_to_dto(self,object,dto_class_type):
        self.mapper.create_map(object.__class__, dto_class_type)
        dto = self.mapper.map(object, dto_class_type)
        return dto