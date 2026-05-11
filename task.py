from __future__ import annotations
import typing
from typing import List

import os
import json
import requests
import logging

logger = logging.getLogger(__name__)

class Task:
    '''Class to manage Synology Download Station tasks.'''
    def __init__(self, ip: str, port: str) -> None:
        logger.debug('ip=%s, port=%s', ip, port)

        self.url = f'http://{ip}:{port}/webapi/DownloadStation/task.cgi'
        self.sid = None

    def __enter__(self, sid: str) -> "Task":
        logger.debug('')

        self.sid = sid

        return self

    def __exit__(
        self,
        exc_type: typing.Any,
        exc_value: typing.Any,
        traceback: typing.Any
    ) -> None:
        logger.debug('')

    def list(self, offset: int = 0, limit: int = -1) -> List[dict]:
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

    def info(self, tasks: List[str]) -> None:
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
        
        session = requests.Session()
        session.cookies.set('id', self.sid)

        if file:
            url = self.url.replace('DownloadStation/task.cgi', 'entry.cgi')
            data = {
                'api': 'SYNO.DownloadStation2.Task',
                'version': '2',
                'method': 'create',
                'type': '"file"',
                'create_list': 'false',
                'file': '["torrent"]'
            }
            if destination:
                data['destination'] = f'"{destination}"'
            else:
                data['destination'] = '""'
                
            with open(file, 'rb') as f:
                files = {
                    'torrent': (
                        os.path.basename(file),
                        f,
                        'application/x-bittorrent'
                    )
                }
                response = session.post(url, data=data, files=files, timeout=30)
                
            if response.status_code == 200:
                res_data = response.json()
                if res_data.get('success'):
                    return True
                else:
                    logger.error(
                        'action=create_fail, error_code=%s, response=%s',
                        res_data.get('error', {}).get('code'),
                        res_data
                    )
                    return False
        else:
            data = {
                'api': 'SYNO.DownloadStation.Task',
                'version': '2',
                'method': 'create',
                'uri': uri
            }
            if destination:
                data['destination'] = destination
                
            response = session.get(self.url, params=data, timeout=30)

            if response.status_code == 200:
                res_data = response.json()
                if res_data.get('success'):
                    return True
                else:
                    logger.error(
                        'action=create_fail, error_code=%s, response=%s',
                        res_data.get('error', {}).get('code'),
                        res_data
                    )
                    return False
            
        logger.error('action=create_fail, status_code=%s', response.status_code)
        return False

    def delete(self, tasks: List[int], force_complete: bool = False) -> None:
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

    def pause(self, tasks: List[str]) -> bool:
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

    def resume(self, tasks: List[str]) -> bool:
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
