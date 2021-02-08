from __future__ import print_function
import os
import importlib
from halo_app.classes import AbsBaseClass


def getit():
    try:
        from flask import current_app as app
        return app.config
    except:
        try:
            module = importlib.import_module(f"{os.getenv('HALO_BASE', 'halo_app')}.config", package=__package__)
            my_class = getattr(module, f"Config_{os.getenv('HALO_STAGE', 'loc')}")
            return my_class
        except Exception as e:
            raise Exception("no settings:" + str(e))

class settingsx(AbsBaseClass):

    def __getattribute__(self, name):
        settings = getit()
        try:
            return settings.get(name)
        except RuntimeError as e:
            print("settingsx=" + name + " error:" + str(e))
            return None

