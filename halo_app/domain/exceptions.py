
from abc import ABCMeta, abstractmethod

from halo_app.exceptions import HaloException


class DomainException(HaloException):
    __metaclass__ = ABCMeta

class BusinessEventMissingSeqException(DomainException):
    pass

class HaloBusinessEventNotImplementedException(DomainException):
    pass

class IllegalBQException(DomainException):
    pass



class NoSuchPathException(DomainException):
    pass


