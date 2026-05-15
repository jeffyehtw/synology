import typing
from typing import Dict
import json
import requests
import logging

logger = logging.getLogger(__name__)

class SynologyAPIError(Exception):
    '''Custom exception for Synology API errors'''
    pass

class Base:
    '''Base class for Synology API interactions.'''
    def __init__(self, ip: str, port: str) -> None:
        logger.debug('ip=%s, port=%s', ip, port)

        self.ip = ip
        self.port = port
        self.session = 'DownloadStation'

    def __enter__(self) -> "Base":
        logger.debug('')

        return self

    def __exit__(
        self,
        exc_type: typing.Any,
        exc_value: typing.Any,
        traceback: typing.Any
    ) -> None:
        logger.debug('')

    def info(self, query: str = 'ALL') -> Dict:
        '''Get API info.'''
        logger.debug('query=%s', query)

        url = f'http://{self.ip}:{self.port}/webapi/query.cgi?'
        params = {
            'api': 'SYNO.API.Info',
            'version': 1,
            'method': 'query',
            'query': query
        }
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        if response.status_code == 200:
            logger.debug(data)

        return data

    def auth(
        self,
        account: str,
        password: str,
        fmt: str = 'cookie',
        opt_code: str = None
    ) -> str:
        '''Authenticate with Synology NAS.'''
        logger.debug('account=%s, password=%s, fmt=%s, opt_code=%s',
            account,
            password,
            fmt,
            opt_code
        )

        url = f'http://{self.ip}:{self.port}/webapi/auth.cgi?'
        params = {
            'api': 'SYNO.API.Auth',
            'version': 3,
            'method': 'login',
            'account': account,
            'passwd': password,
            'session': self.session,
            'format': fmt
        }

        response = requests.get(url, params=params, timeout=30)
        logger.debug(response)
        if response.status_code == 200:
            data = response.json()
            if data.get('success', False):
                logger.debug('sid=%s', data['data']['sid'])
                return data['data']['sid']
            else:
                error_msg = data.get('error', {}).get('errors', 'Authentication failed')
                logger.error('action=auth, success=false, error=%s', error_msg)
                raise SynologyAPIError(f'Synology auth failed: {error_msg}')
        else:
            logger.error('action=auth, status=%d', response.status_code)
            raise SynologyAPIError(
                f'Synology auth request failed with status '
                f'{response.status_code}'
            )

    def logout(self) -> None:
        logger.debug('')

        url = f'http://{self.ip}:{self.port}/webapi/auth.cgi?'
        params = {
            'api': 'SYNO.API.Auth',
            'version': 1,
            'method': 'logout',
            'session': self.session
        }

        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        if response.status_code == 200:
            logger.debug(data)
