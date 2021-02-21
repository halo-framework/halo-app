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

class HaloError(Exception):
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


class ConvertDomainExceptionHandler(AbsBaseClass):
    message_service = None

    #@todo add conversion service
    def __init__(self, message_service=None):
        self.message_service = message_service

    def handle(self, de: DomainException) -> AppException:
        #main_message = self.message_service.convert(de.message)
        #detail_message = self.message_service.convert(de.detail)
        return AppException (de.message, de, de.detail,de.data)

class HaloErrorHandler(AbsBaseClass):

    def __init__(self):
        pass

    def handle(self,halo_request,e:Exception,traceback):
        # @todo check if stack needed and working
        e.stack = traceback.format_exc()
        logger.error(e.__str__(), extra=log_json(halo_request.context, {}, e))
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # logger.debug('An Exception occured in '+str(fname)+' lineno: '+str(exc_tb.tb_lineno)+' exc_type '+str(exc_type)+' '+e.message)
        return e


class HaloExceptionHandler(AbsBaseClass):

    def __init__(self):
        pass

    def handle(self,halo_request,e:Exception,traceback):
        # @todo check if stack needed and working
        e.stack = traceback.format_exc()
        logger.error(e.__str__(), extra=log_json(halo_request.context, {}, e))
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # logger.debug('An Exception occured in '+str(fname)+' lineno: '+str(exc_tb.tb_lineno)+' exc_type '+str(exc_type)+' '+e.message)
        return e


class ExceptionHandler(AbsBaseClass):

    def __init__(self):
        pass

    def handle(self,halo_request,e:Exception,traceback):
        # @todo check if stack needed and working
        e.stack = traceback.format_exc()
        logger.error(e.__str__(), extra=log_json(halo_request.context, {}, e))
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # logger.debug('An Exception occured in '+str(fname)+' lineno: '+str(exc_tb.tb_lineno)+' exc_type '+str(exc_type)+' '+e.message)
        return e
