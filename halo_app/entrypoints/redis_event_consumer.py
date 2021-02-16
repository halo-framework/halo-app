import json
import logging
import redis

from halo_app import bootstrap
from halo_app.classes import AbsBaseClass
from halo_app.entrypoints import client_util
from halo_app.entrypoints.client_type import ClientType
from halo_app.entrypoints.event_consumer import AbsConsumer
from halo_app.sys_util import SysUtil
from halo_app.settingsx import settingsx

settings = settingsx()

logger = logging.getLogger(__name__)


def main():
    logger.info('Redis pubsub starting')
    c = Consumer()

    for m in c.consumer.listen():
        c.handle_command(m)

class Consumer(AbsConsumer):
    def __init__(self):
        super(Consumer,self).__init__()
        r = redis.Redis(settings.REDIS_URI)
        self.consumer = r.pubsub(ignore_subscribe_messages=True)
        self.consumer.subscribe(settings.HALO_CHANNEL)
        client_util.get_halo_context({},client_type=ClientType.event)

if __name__ == '__main__':
    main()
