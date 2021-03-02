
from abc import ABCMeta, abstractmethod

from halo_app.classes import AbsBaseClass
from halo_app.exceptions import AbsHaloException


class AbsDomainException(AbsHaloException):
    __metaclass__ = ABCMeta


class IllegalBQException(AbsDomainException):
    pass



class NoSuchPathException(AbsDomainException):
    pass

