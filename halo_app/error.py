from halo_app.classes import AbsBaseClass


class Error(AbsBaseClass):
    message:str = None
    cause:Exception = None

    def __init__(self,message:str, cause:Exception=None):
      self.message = message
      self.cause = cause