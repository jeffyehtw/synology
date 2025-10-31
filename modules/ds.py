import json
import requests
import logging

from .task import Task

logger = logging.getLogger(__name__)

# Download Station
class DS:
    def __init__(self, ip: str, port: str):
        logger.debug('')
        self.sid = None
        self.task = Task(ip=ip, port=port)

    def __enter__(self, sid: str):
        logger.debug('sid=%s', sid)
        self.sid = sid
        self.task.__enter__(sid=self.sid)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logger.debug('')
