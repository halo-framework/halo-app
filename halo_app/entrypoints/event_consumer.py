import json
import logging

from halo_app import bootstrap
from halo_app.classes import AbsBaseClass
from halo_app.entrypoints import client_util
from halo_app.entrypoints.client_type import ClientType
from halo_app.sys_util import SysUtil
from halo_app.settingsx import settingsx

settings = settingsx()

logger = logging.getLogger(__name__)


class AbsConsumer(AbsBaseClass):
    def __init__(self):
        self.consumer = None
        self.boundary = bootstrap.bootstrap()

    def handle_command(self,m):
        logger.info('handling %s', m)
        data = json.loads(m['data'])
        usecase_id,params,command_id = self.get_from_data(data)
        self.run_command(usecase_id,params,command_id)

    def run_command(self,usecase_id,params,command_id):
        logger.info('start executing command: %s, id: %s ', usecase_id, command_id)
        halo_context = client_util.get_halo_context({},client_type=ClientType.event)
        halo_request = SysUtil.create_command_request(halo_context, usecase_id, params)
        response = self.boundary.execute(halo_request)
        logger.info('executed command: %s, id: %s success: %s', usecase_id,response.request.command.id,response.success)

    def get_from_data(self,data):
        usecase_id = data['usecase_id']
        command_id = data['id']
        params = data
        return usecase_id,params,command_id

