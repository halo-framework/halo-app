from abc import ABCMeta

from halo_app.exceptions import AbsHaloException


class AbsInfraException(AbsHaloException):
    __metaclass__ = ABCMeta

class ApiException(AbsInfraException):
    pass

class MaxTryException(ApiException):
    pass

class MaxTryHttpException(MaxTryException):
    pass


class MaxTryRpcException(MaxTryException):
    pass


class ApiTimeOutExpired(ApiException):
    pass


class DbException(AbsInfraException):
    pass


class DbIdemException(AbsInfraException):
    pass


class CacheException(AbsInfraException):
    pass


class CacheKeyException(CacheException):
    pass

class CacheExpireException(CacheException):
    pass

class ReflectException(AbsInfraException):
    pass


class NoApiDefinitionException(AbsInfraException):
    pass

class ApiClassException(AbsInfraException):
    pass

class NoApiClassException(AbsInfraException):
    pass

class MissingClassConfigException(AbsInfraException):
    pass

class IllegalMethodException(AbsInfraException):
    pass