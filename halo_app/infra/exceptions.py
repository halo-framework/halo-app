from halo_app.exceptions import HaloException


class InfraException(HaloException):
    pass

class ApiException(InfraException):
    pass

class MaxTryException(ApiException):
    pass

class MaxTryHttpException(MaxTryException):
    pass


class MaxTryRpcException(MaxTryException):
    pass


class ApiTimeOutExpired(ApiException):
    pass


class DbException(InfraException):
    pass


class DbIdemException(InfraException):
    pass


class CacheException(InfraException):
    pass


class CacheKeyException(CacheException):
    pass

class CacheExpireException(CacheException):
    pass

class ReflectException(InfraException):
    pass


class NoApiDefinitionException(InfraException):
    pass

class ApiClassException(InfraException):
    pass

class NoApiClassException(InfraException):
    pass

class MissingClassConfigException(InfraException):
    pass

class IllegalMethodException(InfraException):
    pass