import logging
import asyncio
from aiohttp import web
from typing import Dict

from .server import web_handler, proxy_handler
from .websocket_storage import WebsocketStorage


class ServerManager:
    logger_name_base = __name__.split(".")[0]
    _logger = logging.getLogger(f'{logger_name_base}.manager')

    def __init__(self):
        self.runners = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*[runner.cleanup() for runner in self.runners]))

    def __get_logging_params(self, type_name) -> Dict[str, logging.Logger]:
        prefix = f'{self.logger_name_base}.{type_name}'
        return {
            'logger': logging.getLogger(f'{prefix}.server'),
            'access_log': logging.getLogger(f'{prefix}.access')
        }

    async def start_runner(self, runner: web.BaseRunner, host: str, port: int) -> None:
        self.runners.append(runner)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()

    async def start_servers(self, args) -> None:
        # re: logging
        #   web.AppRunner passes kwargs to Server/RequestHandler, but it doesn't set app.logger
        #   web.ServerRunner doesn't pass kwargs to Server/RequestHandler
        #     -> as a workaround, pass to web.Server directly

        # initialize javascript/websocket server
        web_app = web.Application(logger=self.__get_logging_params('webserver')['logger'])
        web_handler.setup_app(web_app)

        # initialize local proxy server
        proxy_server = web.Server(
            None,
            **self.__get_logging_params('proxyserver')
        )
        proxy_handler.setup_server(proxy_server)

        # create websocket storage for sharing websockets between web server and proxy server
        # TODO: this is kinda messy
        storage = WebsocketStorage()
        web_app['websocket_storage'] = storage
        setattr(proxy_server, 'websocket_storage', storage)

        # start both servers
        self._logger.info(f'starting web server')
        await self.start_runner(
            web.AppRunner(
                web_app,
                **self.__get_logging_params('webserver')
            ),
            args.web_host,
            args.web_port
        )
        self._logger.info(f'started web server')

        self._logger.info(f'starting proxy server')
        await self.start_runner(
            web.ServerRunner(proxy_server),
            args.proxy_host,
            args.proxy_port
        )
        self._logger.info(f'started proxy server')
