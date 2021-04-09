import abc
from dataclasses import dataclass
from halo_app.classes import AbsBaseClass

@dataclass
class AbsHaloDto(AbsBaseClass,abc.ABC):

    def __init__(self):
        pass

