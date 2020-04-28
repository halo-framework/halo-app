from __future__ import print_function

import importlib
import logging
from halo_flask.classes import AbsBaseClass
from halo_flask.exceptions import HaloException, ReflectException

logger = logging.getLogger(__name__)

class Reflect(AbsBaseClass):

    @classmethod
    def instantiate(cls,full_class_path,base_class,*args):
        logger.debug("instantiate")
        if full_class_path:
            k = full_class_path.rfind(".")
            if k <= 0:
                raise ReflectException("import class path error:" + full_class_path)
            module_name = full_class_path[:k]
            class_name = full_class_path[k + 1:]
            return cls.do_instantiate(module_name,class_name,base_class,*args)
        raise ReflectException("empty class path error:" + full_class_path)

    @classmethod
    def do_instantiate(cls,module_name,class_name,base_class,*args):
        try:
            module = importlib.import_module(module_name)
        except:
            raise ReflectException("import module error:" + module_name)
        else:
            class_ = getattr(module, class_name)
            if base_class and not issubclass(class_, base_class):
                raise ReflectException("class " + class_name + " is not subclass of " + str(base_class))
            return cls.init_class(class_, *args)

    @classmethod
    def init_class(cls,class_,*args):
        try:
            return class_(*args)
        except Exception as e:
            raise ReflectException("initialize error:" + str(e))
