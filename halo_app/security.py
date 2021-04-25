from __future__ import annotations

import jwt
import logging
import datetime
from halo_app.classes import AbsBaseClass
from halo_app.exceptions import MissingRoleException,MissingSecurityTokenException,BadSecurityTokenException
from halo_app.app.context import HaloContext
from .settingsx import settingsx

logger = logging.getLogger(__name__)

settings = settingsx()

class HaloSecurity(AbsBaseClass):

    token_data  = None
    current_user = None
    user_roles = []

    def __init__(self, request):
        token = None

        if HaloContext.items[HaloContext.ACCESS] in request.headers:
            token = request.headers[HaloContext.items[HaloContext.ACCESS]]

        if not token:
            raise MissingSecurityTokenException('a valid token is missing')

        secret = self.get_secret()

        try:
            self.token_data = jwt.decode(token, secret)
            self.current_user = self.getUser(public_id=self.token_data['public_id'])
            self.user_roles = self.get_user_roles(self.current_user)
        except Exception as e:
            raise BadSecurityTokenException('token is invalid',e)

    def get_secret(self):
        return settings.SECRET_KEY

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
            raise MissingRoleException(str(method_roles))
        return True

    @classmethod
    def user_token(cls, halo_request, public_id, minutes=None,secret=None):

        if not minutes:
            minutes = settings.SESSION_MINUTES

        if not secret:
            secret = settings.SECRET_KEY

        token = jwt.encode(
            {'public_id': public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)},
            secret)
        return {'token': token.decode('UTF-8')}
