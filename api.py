import typing
import logging
from typing import List, Dict, Any, Optional

from .base import Base
from .ds import DS
from base_client import BaseTorrentClient

logger = logging.getLogger(__name__)

class Syno(BaseTorrentClient):
    '''Main Synology API client wrapper.'''
    def __init__(self, ip: str, port: str, account: str, password: str) -> None:
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

    def login(self) -> None:
        self.base.__enter__()
        self.sid = self.base.auth(account=self.account, password=self.password)
        self.ds.__enter__(sid=self.sid)

    def logout(self) -> None:
        self.ds.__exit__(None, None, None)
        self.base.logout()
        self.base.__exit__(None, None, None)

    def __enter__(self) -> "Syno":
        logger.debug('')
        self.login()
        return self

    def __exit__(
        self,
        exc_type: typing.Any,
        exc_value: typing.Any,
        traceback: typing.Any
    ) -> None:
        logger.debug('')
        self.logout()

    def list_tasks(self) -> List[Dict[str, Any]]:
        return self.ds.task.list()

    def create_task(self, uri: Optional[str] = None, file: Optional[str] = None, destination: Optional[str] = None) -> bool:
        return self.ds.task.create(uri=uri, file=file, destination=destination)

    def delete_tasks(self, tasks: List[str]) -> None:
        # Synology delete expects list of ints or strings representing ids
        self.ds.task.delete(tasks=[str(t) for t in tasks])

    def resume_tasks(self, tasks: List[str]) -> bool:
        return self.ds.task.resume(tasks=tasks)

    def pause_tasks(self, tasks: List[str]) -> bool:
        return self.ds.task.pause(tasks=tasks)
