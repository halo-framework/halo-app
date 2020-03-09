from __future__ import print_function

# python
import datetime
import importlib
import logging
import time
from abc import ABCMeta,abstractmethod
import requests
from flask_executor import Executor
from .exceptions import MaxTryHttpException, ApiError



logger = logging.getLogger(__name__)

executor = None

def register_exec(app):
    print("reg executor")
    global executor
    executor = Executor(app)

def get_executor():
    print("get executor")
    global executor
    return executor



