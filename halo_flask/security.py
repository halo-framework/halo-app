from __future__ import print_function

import os
import jwt
import logging
from halo_flask.classes import AbsBaseClass
from halo_flask.exceptions import MissingHaloContextException
from halo_flask.context import HaloContext
from .settingsx import settingsx

logger = logging.getLogger(__name__)

settings = settingsx()

class HaloSecurity(AbsBaseClass):

    token_data  = None
    current_user = None
    user_roles = []

    def __init__(self, request):
        token = None

        if HaloContext.ACCESS in request.headers:
            token = request.headers[HaloContext.ACCESS]

        if not token:
            raise MissingHaloContextException('a valid token is missing')

        try:
            self.token_data = jwt.decode(token, settings.SECRET_KEY)
            self.current_user = self.getUser(public_id=self.token_data['public_id'])
            self.user_roles = self.get_user_roles(self.current_user)
        except:
            raise MissingHaloContextException('token is invalid')

    def getUser(self,public_id):
        return None

    def get_user_roles(self,user):
        return []

    def validate_method(self,method_roles=None):
        if method_roles:
            if self.user_roles:
                for r in method_roles:
                    if r in self.user_roles:
                        return True
            return False
        return True
