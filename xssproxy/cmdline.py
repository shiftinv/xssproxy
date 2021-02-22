import argparse
import logging
import asyncio
from typing import List

from .manager import ServerManager


def parse_args(args: List[str] = None):
    parser = argparse.ArgumentParser(
        prog=__name__.split('.')[0],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('-wh', '--web_host', default='0.0.0.0', help='webserver listen address')
    parser.add_argument('-wp', '--web_port', default=8000, type=int, help='webserver listen port')
    parser.add_argument('-ph', '--proxy_host', default='127.0.0.1', help='proxy listen address')
    parser.add_argument('-pp', '--proxy_port', default=4141, type=int, help='proxy listen port')
    parser.add_argument('-d', '--debug', action='store_true', help='set logging level to debug')

    return parser.parse_args(args)


def run():
    args = parse_args()

    base_logger = logging.getLogger(__name__.split('.')[0])
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s: [%(levelname)s] %(name)s: %(message)s'))
    base_logger.addHandler(handler)
    base_logger.setLevel(logging.DEBUG if args.debug else logging.INFO)
    # logging.basicConfig(level=logging.DEBUG)

    with ServerManager() as mgr:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(mgr.start_servers(args))

        # workaround for ctrl-c on windows
        async def wakeup():
            while True:
                await asyncio.sleep(0.5)
        loop.create_task(wakeup())

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
