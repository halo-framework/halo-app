from __future__ import print_function

from enum import Enum

from halo_app.classes import AbsBaseClass

class ValidError(AbsBaseClass):
    name:str = None
    message:str = None
    cause:Exception = None

    def __init__(self,name:str,message:str, cause:Exception=None):
        self.name = name
        self.message = message
        self.cause = cause

class Notification(AbsBaseClass):
    errors:[ValidError]  = None

    def __init__(self):
        self.errors = []

    def addError(self,message:str,exception:Exception=None):
        self.errors.append(ValidError(message, exception))

    def hasErrors(self)->bool:
        if len(self.errors) > 0:
            return True
        return False

    def errorMessage(self):
        msg = ''
        for i in self.errors:
            msg = msg + i.message + '-' + i.e.message + ','
        return msg
