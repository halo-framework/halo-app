from __future__ import print_function

from abc import ABCMeta

#@todo fix exception parameters
class HaloException(Exception):
    __metaclass__ = ABCMeta
    """
    The abstract exception is used as base template. app expects to handle exception. Accepts the following
    optional arguments:
    """
    def __init__(self, message, detail=None,data=None):
        self.message = message
        self.detail = detail
        self.data = data
    def __str__(self):
        return str(self.message) # __str__() obviously expects a string to be returned, so make sure not to send any other data types


class HaloError(HaloException):
    __metaclass__ = ABCMeta
    """
    The abstract error is used as base template. app does not expect to handle error. Accepts the following
    optional arguments:
    """

    def __init__(self, message, detail=None, data=None):
        self.message = message
        self.detail = detail
        self.data = data

    def __str__(self):
        return str(
            self.message)  # __str__() obviously expects a string to be returned, so make sure not to send any other data types


class AuthException(HaloException):
    pass


class ApiException(HaloException):
    pass


class MaxTryException(ApiException):
    pass


class MaxTryHttpException(MaxTryException):
    pass


class MaxTryRpcException(MaxTryException):
    pass


class ApiTimeOutExpired(ApiException):
    pass


class ApiError(HaloError):
    pass


class DbError(HaloError):
    pass


class DbIdemError(DbError):
    pass


class CacheError(HaloError):
    pass


class CacheKeyError(CacheError):
    pass


class CacheExpireError(CacheError):
    pass

class BadRequestError(HaloError):
    """Custom exception class to be thrown when local request error occurs."""
    def __init__(self, message, detail=None,data=None, http_status=400):
        super(BadRequestError,self).__init__(message, detail,data)
        self.status = http_status

class ServerError(HaloError):
    """Custom exception class to be thrown when local server error occurs."""
    def __init__(self, message, detail=None,data=None, http_status=500):
        super(ServerError, self).__init__(message, detail, data)
        self.status = http_status

class ProviderError(HaloError):
    pass

class NoLocalSSMClass(HaloError):
    pass

class NoLocalSSMModule(HaloError):
    pass

class BusinessEventMissingSeqException(HaloException):
    pass

class HaloMethodNotImplementedException(HaloException):
    pass

class IllegalBQException(HaloException):
    pass

class NoApiDefinition(HaloException):
    pass

class ApiClassErrorException(HaloException):
    pass

class NoApiClassException(HaloException):
    pass

class StoreException(HaloException):
    pass

class StoreClearException(HaloException):
    pass

class MissingHaloContextException(HaloException):
    pass

class NoCorrelationIdException(HaloException):
    pass

class ReflectException(HaloException):
    pass