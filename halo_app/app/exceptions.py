from abc import ABCMeta, abstractmethod

from halo_app.classes import AbsBaseClass
from halo_app.domain.exceptions import DomainException
from halo_app.exceptions import HaloError, HaloException


class AppException(HaloException):
    __metaclass__ = ABCMeta

class AppError(HaloError):
    __metaclass__ = ABCMeta

class BadRequestError(AppError):
    pass

class ServerError(AppError):
    pass

class AuthError(AppError):
    pass

class MissingMethodIdError(AppError):
    pass

class CommandNotMappedError(AppError):
    pass

class QueryNotMappedError(AppError):
    pass

class MissingResponsetoClientTypeError(AppError):
    pass

class MissingHaloContextException(AppException):
    pass

class NoCorrelationIdException(AppException):
    pass

class HaloMethodNotImplementedException(AppException):
    pass

class BusinessEventMissingSeqException(AppException):
    pass

class BusinessEventNotImplementedException(AppException):
    pass

class HaloRequestError(HaloError):
    pass


class ConvertDomainExceptionHandler(AbsBaseClass):
    message_service = None

    #@todo add conversion service
    def __init__(self, message_service=None):
        self.message_service = message_service

    def handle(self, de: DomainException) -> AppException:
        #main_message = self.message_service.convert(de.message)
        #detail_message = self.message_service.convert(de.detail)
        return AppException ( de.message, de, de.detail,de.data)