import uuid
import datetime
from halo_app.classes import AbsBaseClass


class Error(AbsBaseClass):
    message:str = None
    cause:Exception = None

    def __init__(self,message:str, cause:Exception=None):
        self.message = message
        self.cause = cause

class HaloError(AbsBaseClass):
    id:str = None
    timestamp:datetime.datetime = None
    code: str = None
    message: str = None
    errors: [Error] = None

    def __init__(self, code: str, message: str, errors: [Error] = None):
        self.id = uuid.uuid4().__str__()
        self.timestamp = datetime.datetime.now().timestamp()
        self.code = code
        self.message = message
        self.errors = errors

