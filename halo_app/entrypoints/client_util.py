from halo_app.app.context import HaloContext
from halo_app.app.utilx import Util
from halo_app.entrypoints.client_type import ClientType


def get_halo_context(headers=None,env={},client_type:ClientType=ClientType.api):
    context = Util.init_halo_context(env)
    if headers:
        for i in headers.keys():
            if type(i) == str:
                context.put(i.lower(), headers[i])
    context.put(HaloContext.client_type, client_type)
    return context
