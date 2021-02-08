import inspect
from typing import Callable

from halo_app.classes import AbsBaseClass
from halo_app.app.uow import AbsUnitOfWork
from halo_app.app.boundary import BoundaryService
from halo_app.infra.event_publisher import AbsPublisher
from halo_app.reflect import Reflect
from halo_app.settingsx import settingsx

settings = settingsx()

def bootstrap(
    start_orm: bool = settings.START_ORM,#True,
    uow: AbsUnitOfWork = Reflect.instantiate(settings.UOW_CLASS,AbsUnitOfWork),#SqlAlchemyUnitOfWork(),
    publish: Callable = Reflect.instantiate(settings.PUBLISHER_CLASS,AbsPublisher),#Publisher(),
) -> BoundaryService:

    if start_orm:
        from halo_app.infra.orm import clear_mappers
        clear_mappers()
        start_mappers = Reflect.import_method_from(settings.ORM_METHOD)
        start_mappers()

    dependencies = {'uow': uow, 'publish': publish}
    for item in settings.DEPENDENCIES:
        clazz = settings.DEPENDENCIES[item]
        dependencies[item] = Reflect.instantiate(clazz)

    injected_event_handlers = {
        event_type: [
            inject_dependencies(handler, dependencies)
            for handler in event_handlers
        ]
        for event_type, event_handlers in EVENT_HANDLERS.items()
    }
    injected_command_handlers = {
        command_type: inject_dependencies(handler, dependencies)
        for command_type, handler in COMMAND_HANDLERS.items()
    }
    injected_query_handlers = {
        query_type: inject_dependencies(handler, dependencies)
        for query_type, handler in QUERY_HANDLERS.items()
    }

    return BoundaryService(
        uow=uow,
        publisher = publish,
        event_handlers=injected_event_handlers,
        command_handlers=injected_command_handlers,
        query_handlers=injected_query_handlers,
    )


def inject_dependencies(handler, dependencies):
    params = inspect.signature(handler).parameters
    deps = {
        name: dependency
        for name, dependency in dependencies.items()
        if name in params
    }
    return lambda message: handler(message, **deps)


EVENT_HANDLERS = {

}

COMMAND_HANDLERS = {

}

QUERY_HANDLERS = {

}