from __future__ import print_function

import configparser
import datetime
import json
import logging
import os
import time
import uuid
from abc import ABCMeta,abstractmethod

#@ TODO put_parameter should be activated only is current value is different then the existing one
#@ TODO perf activation will reload SSM if needed and refresh API table


from .ssm.onprem_ssm  import set_app_param_config as set_app_param_config_onprem
from .ssm.onprem_ssm import get_config as get_config_onprem
from .ssm.onprem_ssm import get_app_config as get_app_config_onprem
from ..settingsx import settingsx
from halo_flask.exceptions import ProviderError
from halo_flask.classes import AbsBaseClass
from halo_flask.logs import log_json
from halo_flask.sys_util import SysUtil

settings = settingsx()
#current_milli_time = lambda: int(round(time.time() * 1000))

logger = logging.getLogger(__name__)

AWS = 'AWS'
AZURE = 'AZURE'
GCP = 'GCP'
KUBELESS = 'KUBELESS'
ONPREM = 'ONPREM'
PROVIDERS = [AWS,AZURE,GCP,KUBELESS]


def get_provider_name():
    if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
        return AWS
    if 'KUBELESS_FUNCTION_NAME' in os.environ:
        return KUBELESS
    if settings.PROVIDER and settings.PROVIDER in PROVIDERS:
        return settings.PROVIDER
    return ONPREM


class ONPREMProvider(AbsBaseClass):
    __metaclass__ = ABCMeta

    PROVIDER_NAME = ONPREM

    @abstractmethod
    def show(self):
        raise NotImplementedError

    @abstractmethod
    def get_context(self):
        return {"stage": SysUtil.get_stage()}

    @abstractmethod
    def get_header_name(self,request,name):
        return name

    @abstractmethod
    def get_request_id(self,request):
        return uuid.uuid4().__str__()




provider = None
def get_provider():
    global provider
    if provider:
        return provider
    provider_name = get_provider_name()
    logger.info("provider_name:"+str(provider_name))
    if  provider_name == AWS:
        try:
            from halo_aws.providers.cloud.aws.aws import AWSProvider
            provider = AWSProvider()
        except Exception as e:
            raise ProviderError(e)
    else:
        provider = ONPREMProvider()
    return provider


################## ssm ###########################

def set_app_param_config(ssm_type, host):
    """

    :param region_name:
    :param host:
    :return:
    """
    if ssm_type == AWS:
        try:
            from .ssm.aws_ssm import set_app_param_config as set_app_param_config_cld
            return set_app_param_config_cld(host)
        except Exception as e:
            raise ProviderError(e)
    return set_app_param_config_onprem(host)



def get_config(ssm_type):
    """

    :param region_name:
    :return:
    """
    # Initialize app if it doesn't yet exist
    if ssm_type == AWS:
        try:
            from .ssm.aws_ssm import get_config as get_config_cld
            return get_config_cld()
        except Exception as e:
            raise ProviderError(e)
    return get_config_onprem()


def get_app_config(ssm_type):
    """

    :param region_name:
    :return:
    """
    # Initialize app if it doesn't yet exist
    if ssm_type == AWS:
        try:
            from .ssm.aws_ssm import get_app_config as get_app_config_cld
            return get_app_config_cld()
        except Exception as e:
            raise ProviderError(e)
    return get_app_config_onprem()

