import abc

from halo_app.classes import AbsBaseClass
from halo_app.error import HaloError, Error


class Result(AbsBaseClass):
    # only for command

    error:HaloError = None
    payload = None
    success:bool = None
    failure:bool = None

    def __init__(self,code=None,message=None,error_message=None,exception=None,payload=None):
        if message:
            the_error = Error(error_message, exception)
            self.error = HaloError(code,message,[the_error])
            self.failure = True
            self.success = not self.failure
        else:
            self.payload = payload
            self.success = True
            self.failure = not self.success

    @staticmethod
    def fail(code:str,message:str,err_message:str,exception:Exception=None):
        return Result(code=code,message=message,error_message=err_message,exception=exception)

    @staticmethod
    def ok(payload=None):
        return Result(payload=payload)
