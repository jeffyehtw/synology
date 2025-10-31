from __future__ import annotations

import json
import requests
import logging

logger = logging.getLogger(__name__)

class Task:
    def __init__(self, ip: str, port: str):
        logger.debug('')
        self.url = f'http://{ip}:{port}/webapi/DownloadStation/task.cgi?'
        self.sid = None

    def __enter__(self, sid: str):
        logger.debug('')
        self.sid = sid
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logger.debug('')

    def list(self, offset: int = 0, limit: int = -1) -> list[dict]:
        logger.debug('')
        params = {
            'api': 'SYNO.DownloadStation.Task',
            'version': 1,
            'method': 'list',
            'offset': offset,
            'limit': limit,
            'additional': 'detail,transfer,file,tracker,peer',
            '_sid': self.sid
        }
        response = requests.get(self.url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data['data']['tasks']

        return None

    def info(self, tasks: list[str]) -> None:
        logger.debug('tasks=[%s]', ','.join(tasks))

    def create(
            self,
            uri: str,
            file: str,
            unzip_password: str = None,
            destination: str = None
        ) -> None:
        logging.debug(
            'uri=%s, file=%s, unzip_password=%s, dst=%s',
            uri,
            file,
            unzip_password,
            dst
        )

    def delete(self, tasks: list[int], force_complete: bool = False) -> None:
        logger.debug(
            'tasks=[%s], force_complete=%d',
            ','.join(tasks),
            force_complete
        )

        params = {
            'api': 'SYNO.DownloadStation.Task',
            'version': 1,
            'method': 'delete',
            'id': ','.join(tasks),
            'force_complete': 'true' if force_complete else 'false',
            '_sid': self.sid
        }
        response = requests.get(self.url, params=params)
        if response.status_code == 200:
            logger.debug(response)

    def pause(self, tasks: str) -> None:
        logger.debug('tasks=[%s]', ','.join(tasks))

    def resume(self, tasks: str) -> None:
        logger.debug('tasks=[%s]', ','.join(tasks))

    def resume(self, tasks: str, destination: str) -> None:
        logger.debug('tasks=[%s], destination=%s', ','.join(tasks), destination)
