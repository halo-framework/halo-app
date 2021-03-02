import abc

from halo_app.classes import AbsBaseClass
from halo_app.error import Error


class Result(AbsBaseClass):
    # only for command

    error:Error = None
    payload = None
    success:bool = None
    failure:bool = None

    def __init__(self,message=None,exception=None,payload=payload):
        if message:
            self.error = Error(message, exception)
            self.failure = True
            self.success = not self.failure
        else:
            self.payload = payload
            self.success = True
            self.failure = not self.success

    @staticmethod
    def fail(message:str,exception:Exception=None):
        return Result(message=message,exception=exception)

    @staticmethod
    def ok(payload=None):
        return Result(payload=payload)
