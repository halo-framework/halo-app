from __future__ import print_function

# python
import abc
import datetime
import logging
import traceback
from abc import ABCMeta,abstractmethod
# app
from halo_app.app.exceptions import HaloError, CommandNotMappedError, HaloException, QueryNotMappedError
from .utilx import Util
from ..const import SYSTEMChoice, LOGChoice, ERRType
from ..logs import log_json
from ..reflect import Reflect
from halo_app.app.request import AbsHaloRequest, HaloCommandRequest, HaloEventRequest, HaloQueryRequest
from halo_app.app.response import AbsHaloResponse, HaloResponseFactory
from ..classes import AbsBaseClass
from ..settingsx import settingsx

settings = settingsx()

logger = logging.getLogger(__name__)

class IBoundaryService(AbsBaseClass, abc.ABC):
    """
    the only port exposed from the boundry
    """
    @abc.abstractmethod
    def execute(self, halo_request: AbsHaloRequest)->AbsHaloResponse:
        pass

class BoundaryService(IBoundaryService):

    """
        the only point of communication with left-side driver
        adapters. It accepts commands, and calls the appropriate command handler.

        Requires token authentication.
        Only admin users are able to access this view.
        """

    def __init__(self, uow,publisher,event_handlers,command_handlers,query_handlers):
        super(BoundaryService, self).__init__()
        self.uow = uow
        self.publisher = publisher
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers
        self.query_handlers = query_handlers

    def execute(self, halo_request: AbsHaloRequest)->AbsHaloResponse:
        """

        :param vars:
        :return:
        """
        now = datetime.datetime.now()
        error_message = None
        error = None
        orig_log_level = 0

        try:
            if isinstance(halo_request, HaloEventRequest) or issubclass(halo_request.__class__, HaloEventRequest):
                raise HaloError(f'{halo_request} was not a Query or Command request')
            ret = self.__process(halo_request)
            total = datetime.datetime.now() - now
            logger.info(LOGChoice.performance_data.value, extra=log_json(halo_request.context,
                                                                         {LOGChoice.type.value: SYSTEMChoice.server.value,
                                                            LOGChoice.milliseconds.value: int(total.total_seconds() * 1000)}))
            return ret

        except HaloError as e:
            error = e
            error.type = ERRType.error
            error_message = str(error)
            # @todo check if stack needed and working
            e.stack = traceback.format_exc()
            logger.error(error_message, extra=log_json(halo_request.context, halo_request.vars, e))
            # exc_type, exc_obj, exc_tb = sys.exc_info()
            # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            # logger.debug('An error occured in '+str(fname)+' lineno: '+str(exc_tb.tb_lineno)+' exc_type '+str(exc_type)+' '+e.message)

        except HaloException as e:
            error = e
            error.type = ERRType.exception
            error_message = str(error)
            # @todo check if stack needed and working
            e.stack = traceback.format_exc()
            logger.error(error_message, extra=log_json(halo_request.context, halo_request.vars, e))
            # exc_type, exc_obj, exc_tb = sys.exc_info()
            # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            # logger.debug('An error occured in '+str(fname)+' lineno: '+str(exc_tb.tb_lineno)+' exc_type '+str(exc_type)+' '+e.message)

        except Exception as e:
            error = e
            error.type = ERRType.general
            error_message = str(error)
            #@todo check if stack needed and working
            e.stack = traceback.format_exc()
            logger.error(error_message, extra=log_json(halo_request.context, halo_request.vars, e))
            # exc_type, exc_obj, exc_tb = sys.exc_info()
            # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            # logger.debug('An error occured in '+str(fname)+' lineno: '+str(exc_tb.tb_lineno)+' exc_type '+str(exc_type)+' '+e.message)

        finally:
            self.__process_finally(halo_request.context,orig_log_level)

        total = datetime.datetime.now() - now
        logger.info(LOGChoice.error_performance_data.value, extra=log_json(halo_request.context,
                                                                           {LOGChoice.type.value: SYSTEMChoice.server.value,
                                                              LOGChoice.milliseconds.value: int(total.total_seconds() * 1000)}))

        json_error = Util.json_error_response(halo_request.context, halo_request.vars,settings.ERR_MSG_CLASS, error)
        return self.__do_abort(halo_request, errors=json_error)

    def __do_abort(self,halo_request, errors):
        response = HaloResponseFactory().get_halo_response(halo_request,success=False)
        response.errors = errors
        return response

    def __process_finally(self,halo_context, orig_log_level):
        """
        :param orig_log_level:
        """
        if Util.isDebugEnabled(halo_context):
            if logger.getEffectiveLevel() != orig_log_level:
                logger.setLevel(orig_log_level)
                logger.debug("process_finally - back to orig:" + str(orig_log_level),
                             extra=log_json(halo_context))

    def __process(self, halo_request:AbsHaloRequest)->AbsHaloResponse:
        if isinstance(halo_request, HaloQueryRequest) or issubclass(halo_request.__class__, HaloQueryRequest):
            return self.__process_query(halo_request)
        self.queue = [halo_request]
        result = None
        while self.queue:
            message = self.queue.pop(0)
            if isinstance(halo_request,HaloCommandRequest) or issubclass(halo_request.__class__,HaloCommandRequest):
                result = self.__process_command(halo_request)
            elif isinstance(halo_request,HaloEventRequest) or issubclass(halo_request.__class__,HaloEventRequest):
                self.__process_event(message)
            else:
                raise HaloException(f'{message} was not an Event or Command or Query')
        return result


    def _process_event(self, request: HaloEventRequest):
        for handler in self.event_handlers[type(request.event)]:
            try:
                #@todo for attempt in Retrying: implement retry for event failier
                #  configure boundry to retry operations up to three times, with an exponentially increasing wait between attempts
                logger.debug('handling event %s with handler %s', request.event, handler)
                handler(request)
                new_events = self.uow.collect_new_events()
                new_requests = Util.create_requests(new_events)
                self.queue.extend(new_requests)
            except Exception as e:
                logger.exception('Exception %s handling event %s', e,request.event)
                continue

    def __process_event_retry(self, event: HaloEventRequest):
        if type(event) not in self.event_handlers:
            logger.exception('event %s not mapped to handler', type(event))
            return
        for handler in self.event_handlers[type(event)]:
            try:
                #@todo for attempt in Retrying: implement retry for event failier
                #  configure boundry to retry operations up to three times, with an exponentially increasing wait between attempts
                logger.debug('handling event %s with handler %s', event, handler)
                handler.run_event(event)
                new_events = self.uow.collect_new_events()
                new_requests = Util.create_requests(new_events)
                self.queue.extend(new_requests)
            except Exception as e:
                logger.exception('Exception %s handling event %s', e, event)
                continue

    def __process_command(self, command: HaloCommandRequest) -> AbsHaloResponse:
        if settings.ASYNC_MODE:
            return self.__process_async_command(command)
        return self.__process_sync_command(command)

    def __process_sync_command(self, command: HaloCommandRequest)->AbsHaloResponse:
        logger.debug('handling command %s', command)
        if command.method_id not in self.command_handlers:
            raise CommandNotMappedError("command method_id " + command.method_id)
        try:
            # The command dispatcher expects just one handler per command.
            handler = self.command_handlers[command.method_id]
            ret = handler(command)
            if self.uow.items:
                new_events = self.uow.collect_new_events()
                self.queue.extend(new_events)
            return ret
        except Exception as e:
            logger.exception('Exception %s handling command %s',e, command)
            raise

    def __process_async_command(self, command: HaloCommandRequest)->AbsHaloResponse:
        logger.debug('handling command %s', command)
        if command.method_id not in self.command_handlers:
            raise CommandNotMappedError("command method_id " + command.method_id)
        try:
            self.publisher.send(settings.HANDLER_TARGET, command.command)
            return Util.create_response(command,True)
        except Exception as e:
            logger.exception('Exception %s handling command %s',e, command)
            raise

    def __process_query(self, query: HaloQueryRequest)->AbsHaloResponse:
        logger.debug('handling query %s', query)
        if query.method_id not in self.query_handlers:
            raise QueryNotMappedError("query method_id" + query.method_id)
        try:
            # The query dispatcher expects just one handler per command.
            handler = self.query_handlers[query.method_id]
            ret = handler(query)
            return ret
        except Exception as e:
            logger.exception('Exception %s handling query %s',e, query)
            raise


