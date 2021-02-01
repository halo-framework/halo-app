from abc import ABCMeta, abstractmethod

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
