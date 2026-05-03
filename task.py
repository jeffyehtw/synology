from __future__ import annotations

import os
import json
import requests
import logging

logger = logging.getLogger(__name__)

class Task:
    '''Class to manage Synology Download Station tasks.'''
    def __init__(self, ip: str, port: str) -> None:
        logger.debug('ip=%s, port=%s', ip, port)

        self.url = f'http://{ip}:{port}/webapi/DownloadStation/task.cgi?'
        self.sid = None

    def __enter__(self, sid: str):
        logger.debug('')

        self.sid = sid

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logger.debug('')

    def list(self, offset: int = 0, limit: int = -1) -> list[dict]:
        '''List tasks.'''
        logger.debug('offset=%s, limit=%s', offset, limit)

        params = {
            'api': 'SYNO.DownloadStation.Task',
            'version': 1,
            'method': 'list',
            'offset': offset,
            'limit': limit,
            'additional': 'detail,transfer,file,tracker,peer',
            '_sid': self.sid
        }
        response = requests.get(self.url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data['data']['tasks']

        return None

    def info(self, tasks: list[str]) -> None:
        '''Get task info.'''
        logger.debug('tasks=[%s]', ','.join(tasks))

    def create(
            self,
            uri: str = None,
            file: str = None,
            destination: str = None
        ) -> bool:
        '''Create a new download task.'''
        logger.debug(
            'uri=%s, file=%s, destination=%s',
            uri,
            file,
            destination
        )
        params = {
            'api': 'SYNO.DownloadStation.Task',
            'version': 3,
            'method': 'create',
            '_sid': self.sid
        }
        if destination:
            params['destination'] = destination

        if file:
            # For .torrent files, use POST with multipart/form-data
            with open(file, 'rb') as f:
                files = {'file': (os.path.basename(file), f)}
                response = requests.post(self.url, params=params, files=files)
        else:
            # For URIs/magnets
            params['uri'] = uri
            response = requests.get(self.url, params=params)

        if response.status_code == 200:
            data = response.json()
            if not data.get('success', False):
                logger.error('action=create_fail, error_code=%s, response=%s', data.get('error', {}).get('code'), data)
            return data.get('success', False)
        
        logger.error('action=create_fail, status_code=%s', response.status_code)
        return False

    def delete(self, tasks: list[int], force_complete: bool = False) -> None:
        '''Delete tasks.'''
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
        response = requests.get(self.url, params=params, timeout=30)
        if response.status_code == 200:
            logger.debug(response)

    def pause(self, tasks: list[str]) -> bool:
        '''Pause tasks.'''
        logger.debug('tasks=[%s]', ','.join(tasks))

        params = {
            'api': 'SYNO.DownloadStation.Task',
            'version': 1,
            'method': 'pause',
            'id': ','.join(tasks),
            '_sid': self.sid
        }
        response = requests.get(self.url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                logger.debug('Paused %d tasks successfully', len(tasks))
                return True
            else:
                logger.error('Failed to pause tasks: %s', data)
                return False
        return False

    def resume(self, tasks: list[str]) -> bool:
        '''Resume tasks.'''
        logger.debug('tasks=[%s]', ','.join(tasks))

        params = {
            'api': 'SYNO.DownloadStation.Task',
            'version': 1,
            'method': 'resume',
            'id': ','.join(tasks),
            '_sid': self.sid
        }
        response = requests.get(self.url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                logger.debug('Resumed %d tasks successfully', len(tasks))
                return True
            else:
                logger.error('Failed to resume tasks: %s', data)
                return False
        return False
