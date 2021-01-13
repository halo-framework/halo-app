from enum import Enum

from halo_app.classes import AbsBaseClass


class ClientType(AbsBaseClass):

    cli = "CLI"
    api = "API"
    other = "OTHER"
    test = "TEST"