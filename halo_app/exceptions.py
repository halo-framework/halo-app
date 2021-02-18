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

