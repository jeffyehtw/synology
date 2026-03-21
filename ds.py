import json
import requests
import logging

from .task import Task

logger = logging.getLogger(__name__)

class DS:
    '''Download Station module.'''
    def __init__(self, ip: str, port: str) -> None:
        logger.debug('ip=%s, port=%s', ip, port)

        self.sid = None
        self.task = Task(ip=ip, port=port)

    def __enter__(self, sid: str):
        logger.debug('sid=%s', sid)

        self.sid = sid
        self.task.__enter__(sid=self.sid)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logger.debug('')
        
        self.task.__exit__(exc_type, exc_value, traceback)
