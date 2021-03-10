from __future__ import print_function

from enum import Enum

from halo_app.classes import AbsBaseClass
from halo_app.error import Error, HaloError


class ValidError(Error):
    name:str = None

    def __init__(self,name:str,message:str, cause:Exception=None):
        super(ValidError, self).__init__(message,cause)
        self.name = name

class Notification(HaloError):
    errors: [ValidError] = None

    def __init__(self):
        self.errors = []

    def addError(self,name:str,message:str,exception:Exception=None):
        self.errors.append(ValidError(name,message, exception))

    def hasErrors(self)->bool:
        if len(self.errors) > 0:
            return True
        return False


