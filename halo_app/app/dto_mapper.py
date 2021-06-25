import abc
from mapper.object_mapper import ObjectMapper

from halo_app.app.command import AbsHaloCommand
from halo_app.reflect import Reflect
from halo_app.classes import AbsBaseClass


class AbsHaloDtoMapper(AbsBaseClass,abc.ABC):
    mapper = None
    def __init__(self):
        self.mapper = ObjectMapper()

    @abc.abstractmethod
    def map_to_dto(self,object,dto):
        pass

    @abc.abstractmethod
    def map_from_dto(self,dto,object):
        pass

class DtoMapper(AbsHaloDtoMapper):

    def __init__(self):
        super(DtoMapper, self).__init__()

    def map_from_dto(self,dto,object_class_type_name) -> AbsHaloCommand:
        object_class_type = Reflect.instantiate(object_class_type_name,AbsHaloCommand)#Reflect.str2Class(object_class_type_name)
        #self.mapper.create_map(dto.__class__, object_class_type)
        self.mapper.create_map(dto.__class__, object_class_type.__class__)
        object = self.mapper.map(dto, object_class_type)
        return object

    def map_to_dto(self,object,dto_class_type):
        self.mapper.create_map(object.__class__, dto_class_type)
        dto = self.mapper.map(object, dto_class_type)
        return dto