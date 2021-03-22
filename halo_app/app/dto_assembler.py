import abc

from halo_app.app.exceptions import MissingDtoAssemblerException
from halo_app.classes import AbsBaseClass
from halo_app.domain.entity import AbsHaloEntity
from halo_app.dto import AbsHaloDto
from halo_app.reflect import Reflect
from halo_app.settingsx import settingsx
settings = settingsx()

class AbsDtoAssembler(AbsBaseClass, abc.ABC):

    @abc.abstractmethod
    def writeDto(entity:AbsHaloEntity) -> AbsHaloDto:
        pass

    @abc.abstractmethod
    def writeEntity(dto:AbsHaloDto)->AbsHaloEntity:
        pass


class DtoAssemblerFactory(AbsBaseClass):
    @classmethod
    def getAssembler(cls,entity:AbsHaloEntity)->AbsDtoAssembler:
        if type(entity) in settings.ASSEMBLERS:
            dto_assembler_type = settings.ASSEMBLERS[type(entity)]
            assembler:AbsDtoAssembler = Reflect.instantiate(dto_assembler_type, AbsDtoAssembler)
            return assembler
        raise MissingDtoAssemblerException(type(entity))
