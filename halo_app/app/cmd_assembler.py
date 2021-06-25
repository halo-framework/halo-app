import abc
from typing import List, Dict, Callable, Type, TYPE_CHECKING

from halo_app.app.command import AbsHaloCommand
from halo_app.app.exceptions import MissingCmdAssemblerException
from halo_app.app.request import AbsHaloRequest
from halo_app.classes import AbsBaseClass
from halo_app.reflect import Reflect
from halo_app.settingsx import settingsx
from halo_app.app.dto_mapper import DtoMapper

settings = settingsx()

class AbsCmdAssembler(AbsBaseClass, abc.ABC):

    @abc.abstractmethod
    def get_command_type(self,method_id):
        pass

    def write_cmd_for_method(self, method_id: str,data:Dict,flag:str=None) -> AbsHaloCommand:
        mapper = DtoMapper()
        command_class_type = self.get_command_type(method_id)
        cmd = mapper.map_from_dto(data,command_class_type)
        return cmd

class CmdAssemblerFactory(AbsBaseClass):

    @classmethod
    def get_assembler_by_method_id(cls, method_id:str) -> AbsCmdAssembler:
        if method_id in settings.CMD_ASSEMBLERS:
            cmd_assembler_type = settings.CMD_ASSEMBLERS[method_id]
            assembler: AbsCmdAssembler = Reflect.instantiate(cmd_assembler_type, AbsCmdAssembler)
            return assembler
        raise MissingCmdAssemblerException(method_id)

