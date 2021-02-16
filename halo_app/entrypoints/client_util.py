from halo_app.app.context import HaloContext
from halo_app.app.utilx import Util
from halo_app.entrypoints.client_type import ClientType


def get_halo_context(env,client_type:ClientType=ClientType.api):
    context = Util.init_halo_context(env)
    context.put(HaloContext.client_type, client_type)
    return context
