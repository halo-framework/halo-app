
from abc import ABCMeta, abstractmethod

from halo_app.classes import AbsBaseClass
from halo_app.exceptions import HaloException


class DomainException(HaloException):
    __metaclass__ = ABCMeta


class IllegalBQException(DomainException):
    pass



class NoSuchPathException(DomainException):
    pass

