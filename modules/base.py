import json
import requests
import logging

logger = logging.getLogger(__name__)

class Base:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.session = 'cjyeh'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def info(self, query: str = 'ALL') -> None:
        logger.debug('query=%s', query)

        url = f'http://{self.ip}:{self.port}/webapi/query.cgi?'
        params = {
            'api': 'SYNO.API.Info',
            'version': 1,
            'method': 'query',
            'query': query
        }
        response = requests.get(url, params=params)
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

        response = requests.get(url, params=params)
        logger.debug(response)
        if response.status_code == 200:
            data = response.json()
            logger.debug('sid=%s', data['data']['sid'])
        else:
            logger.info('action=exit')
            logger.info('reason=!response')
            exit()

        return data['data']['sid']

    def logout(self) -> None:
        url = f'http://{self.ip}:{self.port}/webapi/auth.cgi?'
        params = {
            'api': 'SYNO.API.Auth',
            'version': 1,
            'method': 'logout',
            'session': self.session
        }

        response = requests.get(url, params=params)
        data = response.json()
        if response.status_code == 200:
            logger.debug(data)
