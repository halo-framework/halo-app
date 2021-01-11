from __future__ import print_function

# python
import abc
import datetime
import logging
import traceback
from abc import ABCMeta,abstractmethod
# app
from ..exceptions import HaloError, CommandNotMappedError, HaloException, QueryNotMappedError
from .utilx import Util
from ..const import SYSTEMChoice, LOGChoice
from ..logs import log_json
from ..reflect import Reflect
from halo_app.app.request import HaloRequest, HaloCommandRequest, HaloEventRequest, HaloQueryRequest
from halo_app.app.response import HaloResponse
from ..classes import AbsBaseClass
from ..settingsx import settingsx

settings = settingsx()

logger = logging.getLogger(__name__)

class AbsBoundaryService(AbsBaseClass,abc.ABC):
    """
    the only port exposed from the boundry
    """
    @abc.abstractmethod
    def execute(self, halo_request: HaloRequest)->HaloResponse:
        pass

class BoundaryService(AbsBoundaryService):

    """
        the only point of communication with left-side driver
        adapters. It accepts commands, and calls the appropriate command handler.

        Requires token authentication.
        Only admin users are able to access this view.
        """

    def __init__(self, uow,event_handlers,command_handlers,query_handlers):
        super(BoundaryService, self).__init__()
        self.uow = uow
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers
        self.query_handlers = query_handlers

    def execute(self, halo_request: HaloRequest)->HaloResponse:
        """

        :param vars:
        :return:
        """
        now = datetime.datetime.now()
        error_message = None
        error = None
        orig_log_level = 0
        http_status_code = 500

        try:
            if isinstance(halo_request, HaloEventRequest) or issubclass(halo_request.__class__, HaloEventRequest):
                raise HaloException(f'{halo_request} was not a Query or Command request')
            ret = self.__process(halo_request)
            total = datetime.datetime.now() - now
            logger.info(LOGChoice.performance_data.value, extra=log_json(halo_request.context,
                                                                         {LOGChoice.type.value: SYSTEMChoice.server.value,
                                                            LOGChoice.milliseconds.value: int(total.total_seconds() * 1000)}))
            return ret

        except HaloError as e:
            http_status_code = e.status_code
            error = e
            error_message = str(error)
            # @todo check if stack needed and working
            e.stack = traceback.format_exc()
            logger.error(error_message, extra=log_json(halo_request.context, halo_request.vars, e))
            # exc_type, exc_obj, exc_tb = sys.exc_info()
            # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            # logger.debug('An error occured in '+str(fname)+' lineno: '+str(exc_tb.tb_lineno)+' exc_type '+str(exc_type)+' '+e.message)

        except Exception as e:
            error = e
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
        return self.__do_abort(halo_request,http_status_code, errors=json_error)

    def __do_abort(self,halo_request,http_status_code, errors):
        ret = HaloResponse(halo_request)
        ret.payload = errors
        ret.code = http_status_code
        ret.headers = {}
        return ret

    def __process_finally(self,halo_context, orig_log_level):
        """
        :param orig_log_level:
        """
        if Util.isDebugEnabled(halo_context):
            if logger.getEffectiveLevel() != orig_log_level:
                logger.setLevel(orig_log_level)
                logger.debug("process_finally - back to orig:" + str(orig_log_level),
                             extra=log_json(halo_context))

    def __process1(self,halo_request:HaloRequest)->HaloResponse:
        if isinstance(halo_request,HaloCommandRequest) or issubclass(halo_request.__class__,HaloCommandRequest):
            return self.run_command(halo_request)
        return self.run_event(halo_request)


    def __process(self,halo_request:HaloRequest)->HaloResponse:
        result = None
        self.queue = [halo_request]
        while self.queue:
            message = self.queue.pop(0)
            if isinstance(halo_request,HaloCommandRequest) or issubclass(halo_request.__class__,HaloCommandRequest):
                result = self.__process_command(halo_request)
            elif isinstance(halo_request,HaloEventRequest) or issubclass(halo_request.__class__,HaloEventRequest):
                self.__process_event(message)
            elif isinstance(halo_request,HaloQueryRequest) or issubclass(halo_request.__class__,HaloQueryRequest):
                self.__process_query(message)
            else:
                raise Exception(f'{message} was not an Event or Command or Query')
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
            except Exception:
                logger.exception('Exception handling event %s', request.event)
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
            except Exception:
                logger.exception('Exception handling event %s', event)
                continue

    def __process_command(self, command: HaloCommandRequest)->HaloResponse:
        logger.debug('handling command %s', command)
        if command.method_id not in self.command_handlers:
            raise CommandNotMappedError("command method_id" + command.method_id)
        try:
            # The command dispatcher expects just one handler per command.
            handler = self.command_handlers[command.method_id]
            ret = handler(command)
            if self.uow.items:
                new_events = self.uow.collect_new_events()
                self.queue.extend(new_events)
            return ret
        except Exception:
            logger.exception('Exception handling command %s', command)
            raise

    def __process_query(self, query: HaloQueryRequest)->HaloResponse:
        logger.debug('handling query %s', query)
        if query.method_id not in self.query_handlers:
            raise QueryNotMappedError("query method_id" + query.method_id)
        try:
            # The query dispatcher expects just one handler per command.
            handler = self.query_handlers[query.method_id]
            ret = handler(query)
            return ret
        except Exception:
            logger.exception('Exception handling query %s', query)
            raise


