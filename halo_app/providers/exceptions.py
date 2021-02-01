from __future__ import print_function

from abc import ABCMeta, abstractmethod



# provider
from halo_app.exceptions import HaloError


class ProviderError(HaloError):
    __metaclass__ = ABCMeta

class SSMError(ProviderError):
    pass

class NoLocalSSMClassError(ProviderError):
    pass

class NoLocalSSMModuleError(ProviderError):
    pass

class NoSSMRegionError(ProviderError):
    pass

class NoSSMDefinedError(ProviderError):
    pass

class NotSSMTypeError(ProviderError):
    pass

class NoONPREMProviderClassError(ProviderError):
    pass

class NoONPREMProviderModuleError(ProviderError):
    pass

class ProviderInitError(ProviderError):
    pass



