from __future__ import print_function

from abc import ABCMeta, abstractmethod


class HaloException(Exception):
    __metaclass__ = ABCMeta
    """The abstract Generic exception for halo"""

    @abstractmethod
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
        return msg  # __str__() obviously expects a string to be returned, so make sure not to send any other view types

class HaloError(HaloException):
    __metaclass__ = ABCMeta
    """
    The abstract error is used as base class for server error with status code. app does not expect to handle error. Accepts the following
    optional arguments:
    """
    error_code = None

    @abstractmethod
    def __init__(self, message, original_exception=None,detail=None, data=None,error_code=None):
        super(HaloError, self).__init__(message, original_exception,detail,data)
        if error_code is not None:
            self.error_code = error_code




"""
class HaloHttpError(HaloError):
    def __init__(self, message, detail=None,view=None, http_status=400):
        super(HaloHttpError,self).__init__(message, detail,view)
        self.status = http_status

class ServerError(HaloHttpError):
    def __init__(self, message, detail=None, view=None, http_status=500):
        super(HaloHttpError, self).__init__(message, detail, view)
        self.status = http_status
"""


class StoreException(HaloException):
    pass

class StoreClearException(HaloException):
    pass



class SecureException(HaloException):
    pass

class MissingRoleException(SecureException):
    pass

class MissingSecurityTokenException(SecureException):
    pass

class BadSecurityTokenException(SecureException):
    pass

class FilterValidationException(SecureException):
    pass

