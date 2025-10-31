import os
import sys
import logging
import argparse
import json

from datetime import datetime, timedelta

from modules.api import API

__description__ = ''
__epilog__ = 'Report bugs to <yehcj.tw@gmail.com>'

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'synology.log'
))
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def load(file: str) -> dict:
    config = None
    if not os.path.exists(file):
        return config
    with open(file, 'r') as fp:
        config = json.load(fp)
    return config

def clean(path: str, tid: str) -> None:
    info = os.path.join(path, f'{tid}.info')
    if os.path.exists(info):
        os.remove(info)
    loaded = os.path.join(path, f'{tid}.torrent.loaded')
    if os.path.exists(loaded):
        os.remove(loaded)

def main():
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog=__epilog__
    )
    parser.add_argument(
        '--ip',
        type=str,
        default=None,
        help='Synology NAS IP address'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Synology NAS port'
    )
    parser.add_argument(
        '--account',
        type=str,
        default=None,
        help='Synology NAS user account'
    )
    parser.add_argument(
        '--password',
        type=str,
        default=None,
        help='Synology NAS user password'
    )
    parser.add_argument(
        '--path',
        type=str,
        default=None,
        help='Directory containing the torrent information files'
    )
    args = parser.parse_args(sys.argv[1:])

    # load configuration file
    config = load(os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'synology.json'
    ))

    # overwrite the configuration if a parameter is provided
    for key, value in vars(args).items():
        if value is None:
            setattr(args, key, config[key])

    with API(
            ip=args.ip,
            port=args.port,
            account=args.account,
            password=args.password
        ) as api:
        items = api.ds.task.list()

        deletes = []
        for item in items:
            tid = item['additional']['detail']['uri'].replace('.torrent', '')
            task = item['id']
            status = item['status']
            logger.debug('tid=%s, task=%s, status=%s', tid, task, status)

            if status == 'seeding':
                clean(path=args.path, tid=tid)
                logger.debug('action=pass')
                continue

            if status == 'downloading' or status == 'seeding':
                file = os.path.join(args.path, f'{tid}.info')
                if not os.path.exists(file):
                    logger.debug('action=pass, reason=!info')
                    continue

                info = None
                with open(file, 'r') as fp:
                    info = json.load(fp)

                if info is None:
                    logger.debug('action=delete, reason=!info')
                    deletes.append(task)
                    continue
                if info['status']['discountEndTime'] is None:
                    logger.debug('action=delete, reason=!endtime')
                    deletes.append(task)
                    continue

                end = datetime.strptime(
                    info['status']['discountEndTime'],
                    '%Y-%m-%d %H:%M:%S'
                )
                now = datetime.now()

                if end - now < timedelta(minutes=5):
                    logger.debug(
                        'end=%s, action=delete, reason=!free',
                        info['status']['discountEndTime']
                    )
                    deletes.append(task)
                    clean(path=args.path, tid=tid)
                else:
                    logger.debug('action=pass, reason=free')

        if len(deletes) > 0:
            api.ds.task.delete(tasks=deletes)

if __name__ == '__main__':
    main()