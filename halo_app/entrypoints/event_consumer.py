import json
import logging
import redis

from halo_app import bootstrap
from halo_app.entrypoints import client_util
from halo_app.entrypoints.client_type import ClientType
from halo_app.sys_util import SysUtil
from halo_app.settingsx import settingsx

settings = settingsx()

logger = logging.getLogger(__name__)


def main():
    logger.info('Redis pubsub starting')
    r = redis.Redis(settings.REDIS_URI)
    boundary = bootstrap.bootstrap()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(settings.HALO_CHANNEL)
    client_util.get_halo_context(client_type=ClientType.event)

    for m in pubsub.listen():
        handle_command(m, boundary)


def handle_command(m, boundary):
    logger.info('handling %s', m)
    data = json.loads(m['data'])
    method_id,params,command_id = get_from_data(data)
    run_command(method_id,params,boundary)

def run_command(method_id,params,command_id,boundary):
    logger.info('start executing command: %s, id: %s ', method_id, command_id)
    halo_context = client_util.get_halo_context(client_type=ClientType.event)
    halo_request = SysUtil.create_command_request(halo_context, method_id, params)
    response = boundary.execute(halo_request)
    logger.info('executed command: %s, id: %s success: %s', method_id,response.request.command.id,response.success)

def get_from_data(data):
    method_id = data['method_id']
    command_id = data['id']
    params = data
    return method_id,params,command_id


if __name__ == '__main__':
    main()
