from __future__ import annotations

import logging

# from cStringIO import StringIO
# aws
# common

from halo_app.classes import AbsBaseClass
logger = logging.getLogger(__name__)


class ErrorMessages(AbsBaseClass):
    hashx = {}
    # generic halo messages and proprietery api messages
    hashx["MaxTryException"] = {"code": 10100, "message": "Api reached Max Try count"}
    hashx["MaxTryHttpException"] = {"code": 10101, "message": "Api reached Max Try count using http"}
    hashx["MaxTryRpcException"] = {"code": 10102, "message": "Api reached Max Try count using rpc"}
    hashx["ApiTimeOutExpired"] = {"code": 10103, "message": "Api call Timed Out"}
    hashx["ApiError"] = {"code": 10104, "message": "Api call Error"}
    hashx["ConnectionError"] = {"code": 10105, "message": "Api Connection Error"}
    hashx["TypeError"] = {"code": 10106, "message": "Server Type Error"}
    hashx["MissingHaloContextException"] = {"code": 10107, "message": "Missing Halo Context"}
    hashx["MissingSecurityTokenException"] = {"code": 10108, "message": "Missing Halo token"}
    hashx["BadSecurityTokenException"] = {"code": 10109, "message": "Bad Halo token"}


    def get_code(self,ex):
        """
        get the proper status code and error msg for exception
        :param ex:
        :return:
        """
        e = type(ex).__name__
        emsg = str(ex)
        if hasattr(e, 'message'):
            emsg = e.message
        if hasattr(e, 'detail'):
            emsg = e.detail
        if hasattr(e, 'original_exception'):
            emsg = emsg + "["+ str(e.original_exception)+"]"
        logger.debug("e=" + emsg)
        if e in self.hashx:
            code = self.hashx[e]["code"]
            msg = self.hashx[e]["message"]
            dtl = emsg
        else:
            code = 1000
            msg = e
            dtl = ""
            if emsg is not None and emsg != 'None' and emsg != "":
                dtl = emsg
        return code, msg, dtl
