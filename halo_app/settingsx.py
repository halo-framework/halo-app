from __future__ import print_function

from halo_app.classes import AbsBaseClass


def getit():
    try:
        from flask import current_app as app
        return app.config
    except:
        try:
            from ..config import Config
            return Config
        except:
            raise Exception("no settings")

settings = None

class settingsx(AbsBaseClass):

    def __getattribute__(self, name):
        global settings
        if not settings:
            settings = getit()
        try:
            return settings.get(name)
        except RuntimeError as e:
            print("settingsx=" + name + " error:" + str(e))
            return None


"""
try:
    from flask import current_app as app

    class settingsx1(AbsBaseClass):
        def __getattribute__(self, name):
            settings = app.config
            try:
                attr = settings.get(name)
                return attr
            except RuntimeError as e:
                print("settingsx=" + name + " error:" + str(e))
                return None
except:
    from halo_app.config import get_setting

    class settingsx(AbsBaseClass):
        def __getattribute__(self, name):
            settings = get_setting()
            try:
                if hasattr(settings, name):
                    return settings.__getattribute__(name)
                return None
            except RuntimeError as e:
                print("settingsx=" + name + " error:" + str(e))
                return None
"""