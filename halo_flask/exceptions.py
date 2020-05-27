from __future__ import print_function

from abc import ABCMeta, abstractmethod


class HaloException(Exception):
    __metaclass__ = ABCMeta
    """Generic exception for halo"""

    def __init__(self, message, original_exception=None, detail=None,data=None):
        super(HaloException, self).__init__()
        self.message = message
        self.original_exception = original_exception
        self.detail = detail
        self.data = data

    def __str__(self):
        msg = str(self.message)
        if self.original_exception:
            msg = msg + " ,original:" +str(self.original_exception)
        return msg  # __str__() obviously expects a string to be returned, so make sure not to send any other data types

class HaloError(HaloException):
    __metaclass__ = ABCMeta
    """
    The abstract error is used as base class. app does not expect to handle error. Accepts the following
    optional arguments:
    """
    status_code = 400

    def __init__(self, message, original_exception=None,detail=None, data=None,status_code=None):
        super(HaloError, self).__init__(message, original_exception,detail,data)
        if status_code is not None:
            self.status_code = status_code

class BadRequestError(HaloError):
    pass

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

"""
class HaloHttpError(HaloError):
    def __init__(self, message, detail=None,data=None, http_status=400):
        super(HaloHttpError,self).__init__(message, detail,data)
        self.status = http_status

class ServerError(HaloHttpError):
    def __init__(self, message, detail=None, data=None, http_status=500):
        super(HaloHttpError, self).__init__(message, detail, data)
        self.status = http_status
"""

class ProviderError(HaloError):
    pass

class SSMError(HaloError):
    pass

class NoLocalSSMClassError(HaloError):
    pass

class NoLocalSSMModuleError(HaloError):
    pass

class NoSSMRegionError(HaloError):
    pass

class BusinessEventMissingSeqException(HaloException):
    pass

class HaloMethodNotImplementedException(HaloException):
    pass

class IllegalBQException(HaloException):
    pass

class NoApiDefinitionError(HaloError):
    pass

class ApiClassError(HaloError):
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

class NoSSMDefinedError(HaloError):
    pass

class NotSSMTypeError(HaloError):
    pass

class NoONPREMProviderClassError(HaloError):
    pass

class NoONPREMProviderModuleError(HaloError):
    pass

class ProviderInitError(HaloError):
    pass