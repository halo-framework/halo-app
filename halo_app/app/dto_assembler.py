import abc
from typing import List, Dict, Callable, Type, TYPE_CHECKING

from halo_app.app.exceptions import MissingDtoAssemblerException
from halo_app.app.request import AbsHaloRequest
from halo_app.classes import AbsBaseClass
from halo_app.domain.entity import AbsHaloEntity
from halo_app.app.dto import AbsHaloDto
from halo_app.reflect import Reflect
from halo_app.settingsx import settingsx
from halo_app.sys_util import SysUtil

settings = settingsx()

class AbsDtoAssembler(AbsBaseClass, abc.ABC):

    @abc.abstractmethod
    def write_dto(self,entity:AbsHaloEntity) -> AbsHaloDto:
        pass

    @abc.abstractmethod
    def write_entity(self,dto:AbsHaloDto)->AbsHaloEntity:
        pass

    @abc.abstractmethod
    def write_dto_for_method(self, method_id: str,data:Dict,flag:str=None) -> AbsHaloDto:
        pass

class DtoAssemblerFactory(AbsBaseClass):

    @classmethod
    def get_assembler_by_request(cls, request: AbsHaloRequest) -> AbsDtoAssembler:
        if request.method_id in settings.DTO_ASSEMBLERS:
            dto_assembler_type = settings.DTO_ASSEMBLERS[request.method_id]
            assembler: AbsDtoAssembler = Reflect.instantiate(dto_assembler_type, AbsDtoAssembler)
            return assembler
        raise MissingDtoAssemblerException(request.method_id)

    @classmethod
    def get_assembler_by_entity(cls,entity:AbsHaloEntity)->AbsDtoAssembler:
        entity_type = SysUtil.instance_full_name(entity)
        if entity_type in settings.DTO_ASSEMBLERS:
            dto_assembler_type = settings.DTO_ASSEMBLERS[entity_type]
            assembler:AbsDtoAssembler = Reflect.instantiate(dto_assembler_type, AbsDtoAssembler)
            return assembler
        raise MissingDtoAssemblerException(entity_type)

    @classmethod
    def get_assembler_by_dto(cls,dto:AbsHaloDto)->AbsDtoAssembler:
        dto_type = SysUtil.instance_full_name(dto)
        if dto_type in settings.DTO_ASSEMBLERS:
            dto_assembler_type = settings.DTO_ASSEMBLERS[dto_type]
            assembler:AbsDtoAssembler = Reflect.instantiate(dto_assembler_type, AbsDtoAssembler)
            return assembler
        raise MissingDtoAssemblerException(dto_type)