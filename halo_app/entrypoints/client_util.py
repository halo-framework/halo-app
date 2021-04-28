from halo_app.app.context import HaloContext
from halo_app.app.utilx import Util
from halo_app.entrypoints.client_type import ClientType


def get_halo_context(env,http_request=None,client_type:ClientType=ClientType.api):
    context = Util.init_halo_context(env)
    context.put(HaloContext.client_type, client_type)
    if http_request:
        context.put(HaloContext.path, http_request.path)
        context.put(HaloContext.method, http_request.method)
    return context
