import logging

from .base import Base
from .ds import DS

logger = logging.getLogger(__name__)

class API:
    def __init__(self, ip: str, port: str, account: str, password: str):
        logger.debug('ip=%s, port=%s, account=%s, password=%s',
            ip,
            port,
            account,
            password
        )
        self.ip = ip
        self.port = port
        self.account = account
        self.password = password
        self.sid = None
        self.base = Base(ip=ip, port=port)
        self.ds = DS(ip=ip, port=port)

    def __enter__(self):
        logger.debug('')
        self.base.__enter__()
        self.sid = self.base.auth(account=self.account, password=self.password)
        self.ds.__enter__(sid=self.sid)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logger.debug('')
