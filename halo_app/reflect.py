from __future__ import annotations
import sys
import importlib
import logging
from halo_app.classes import AbsBaseClass
from halo_app.infra.exceptions import  ReflectException

logger = logging.getLogger(__name__)

class Reflect(AbsBaseClass):

    @classmethod
    def instantiate(cls,full_class_path,base_class,*args):
        logger.debug("instantiate")
        if full_class_path:
            module_name, class_name = cls.__break_full_class_path(full_class_path)
            return cls.do_instantiate(module_name,class_name,base_class,*args)
        raise ReflectException("empty class path error:" + full_class_path)

    @classmethod
    def __break_full_class_path(cls,full_class_path):
        k = full_class_path.rfind(".")
        if k <= 0:
            raise ReflectException("import class path error:" + full_class_path)
        module_name = full_class_path[:k]
        class_name = full_class_path[k + 1:]
        return module_name,class_name

    @classmethod
    def do_instantiate(cls,module_name,class_name,base_class,*args):
        try:
            module = importlib.import_module(module_name)
        except Exception as e:
            raise ReflectException("import module error:" + str(e) + " for module:"+ module_name,e)
        else:
            try:
                class_ = getattr(module, class_name)
            except Exception as e:
                raise ReflectException("import class error:" + str(e) + " for class:" + class_name,e)
            if base_class and not issubclass(class_, base_class):
                raise ReflectException("class " + class_name + " is not subclass of " + str(base_class))
            try:
                return cls.__init_class(class_, *args)
            except Exception as e:
                raise ReflectException("import class error:" + str(e) + " for class:" + class_name,e)

    @classmethod
    def __init_class(cls,class_,*args):
        try:
            return class_(*args)
        except Exception as e:
            raise ReflectException("initialize error:" + str(e),e)

    @classmethod
    def import_method_from(cls,full_class_path):
        # import_from("abc.def.ghi.jkl.myfile", "mymethod")
        module_name, method_name = cls.__break_full_class_path(full_class_path)
        module = __import__(module_name, fromlist=[method_name])
        return getattr(module, method_name)

    @classmethod
    def str2Class(cls,path):
        module_name, class_name = cls.__break_full_class_path(path)
        return getattr(sys.modules[module_name], class_name)