from abc import ABCMeta, abstractmethod
import logging
from halo_app.classes import AbsBaseClass
from halo_app.domain.exceptions import DomainException
from halo_app.exceptions import HaloException
from halo_app.logs import log_json

logger = logging.getLogger(__name__)

class AppException(HaloException):
    __metaclass__ = ABCMeta

class AuthException(AppException):
    pass

class MissingMethodIdException(AppException):
    pass

class CommandNotMappedException(AppException):
    pass

class QueryNotMappedException(AppException):
    pass

class MissingResponsetoClientTypeException(AppException):
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

class HaloRequestException(AppException):
    pass

class HttpFailException(AppException):
    pass

class AppValidationException(AppException):
    pass

class EngineException(AppException):
    pass


class ConvertDomainExceptionHandler(AbsBaseClass):
    message_service = None

    #@todo add conversion service
    def __init__(self, message_service=None):
        self.message_service = message_service

    def handle(self, de: DomainException) -> AppException:
        #main_message = self.message_service.convert(de.message)
        #detail_message = self.message_service.convert(de.detail)
        return AppException (de.message, de, de.detail,de.data)
