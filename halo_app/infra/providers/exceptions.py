from __future__ import annotations

from abc import ABCMeta, abstractmethod



# provider
from halo_app.infra.exceptions import AbsInfraException


class ProviderException(AbsInfraException):
    __metaclass__ = ABCMeta

class SSMException(ProviderException):
    pass

class NoLocalSSMClassException(ProviderException):
    pass

class NoLocalSSMModuleException(ProviderException):
    pass

class NoSSMRegionException(ProviderException):
    pass

class NoSSMDefinedException(ProviderException):
    pass

class NotSSMTypeException(ProviderException):
    pass

class NoONPREMProviderClassException(ProviderException):
    pass

class NoONPREMProviderModuleException(ProviderException):
    pass

class ProviderInitException(ProviderException):
    pass



