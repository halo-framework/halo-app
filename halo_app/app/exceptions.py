from abc import ABCMeta, abstractmethod
import logging
from halo_app.classes import AbsBaseClass
from halo_app.domain.exceptions import AbsDomainException
from halo_app.exceptions import AbsHaloException, AbsExceptionHandler
from halo_app.logs import log_json

logger = logging.getLogger(__name__)

class AbsAppException(AbsHaloException):
    __metaclass__ = ABCMeta

class AuthException(AbsAppException):
    pass

class MissingMethodIdException(AbsAppException):
    pass

class CommandNotMappedException(AbsAppException):
    pass

class QueryNotMappedException(AbsAppException):
    pass

class MissingResponsetoClientTypeException(AbsAppException):
    pass

class MissingHaloContextException(AbsAppException):
    pass

class NoCorrelationIdException(AbsAppException):
    pass

class HaloMethodNotImplementedException(AbsAppException):
    pass

class BusinessEventMissingSeqException(AbsAppException):
    pass

class BusinessEventNotImplementedException(AbsAppException):
    pass

class HaloRequestException(AbsAppException):
    pass

class HttpFailException(AbsAppException):
    pass

class AppValidationException(AbsAppException):
    pass

class EngineException(AbsAppException):
    pass

class MissingDtoAssemblerException(AbsAppException):
    pass


class ConvertDomainExceptionHandler(AbsExceptionHandler):
    message_service = None

    #@todo add conversion service
    def __init__(self, message_service=None):
        self.message_service = message_service

    def handle(self, de: AbsDomainException) -> AbsAppException:
        #main_message = self.message_service.convert(de.message)
        #detail_message = self.message_service.convert(de.detail)
        return AbsAppException (de.message, de, de.detail, de.data)
