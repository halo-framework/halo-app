from dataclasses import dataclass

from halo_app.classes import AbsBaseClass

@dataclass
class AbsHaloDto(AbsBaseClass):
    id = None

    def __init__(self, id: str):
        self.id = id

