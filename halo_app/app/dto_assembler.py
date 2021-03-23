import abc

from halo_app.app.exceptions import MissingDtoAssemblerException
from halo_app.classes import AbsBaseClass
from halo_app.domain.entity import AbsHaloEntity
from halo_app.dto import AbsHaloDto
from halo_app.reflect import Reflect
from halo_app.settingsx import settingsx
from halo_app.sys_util import SysUtil

settings = settingsx()

class AbsDtoAssembler(AbsBaseClass, abc.ABC):

    @abc.abstractmethod
    def writeDto(self,entity:AbsHaloEntity) -> AbsHaloDto:
        pass

    @abc.abstractmethod
    def writeEntity(self,dto:AbsHaloDto)->AbsHaloEntity:
        pass

class DtoAssemblerFactory(AbsBaseClass):

    @classmethod
    def getAssembler(cls,entity:AbsHaloEntity)->AbsDtoAssembler:
        if type(entity) in settings.ASSEMBLERS:
            dto_assembler_type = settings.ASSEMBLERS[type(entity)]
            assembler:AbsDtoAssembler = Reflect.instantiate(dto_assembler_type, AbsDtoAssembler)
            return assembler
        raise MissingDtoAssemblerException(type(entity))

    @classmethod
    def getAssembler(cls,dto:AbsHaloDto)->AbsDtoAssembler:
        dto_type = SysUtil.instance_full_name(dto)
        if dto_type in settings.ASSEMBLERS:
            dto_assembler_type = settings.ASSEMBLERS[dto_type]
            assembler:AbsDtoAssembler = Reflect.instantiate(dto_assembler_type, AbsDtoAssembler)
            return assembler
        raise MissingDtoAssemblerException(dto_type)