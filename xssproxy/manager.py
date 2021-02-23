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

    async def start_runner(self, runner: web.BaseRunner, host: str, port: int, log_name: str) -> None:
        self._logger.info(f'starting {log_name} on {host}:{port}')
        self.runners.append(runner)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        self._logger.info(f'started {log_name}')

    async def start_servers(self, args) -> None:
        # re: logging
        #   web.AppRunner passes kwargs to Server/RequestHandler, but it doesn't set app.logger
        #   web.ServerRunner doesn't pass kwargs to Server/RequestHandler
        #     -> as a workaround, pass to web.Server directly

        # initialize javascript/websocket server
        web_logger_params = self.__get_logging_params('web')
        web_app = web.Application(logger=web_logger_params['logger'])
        web_handler.setup_app(web_app)

        # initialize local proxy server
        proxy_server = web.Server(
            None,
            **self.__get_logging_params('proxy')
        )
        proxy_handler.setup_server(proxy_server)

        # create websocket storage for sharing websockets between web server and proxy server
        # TODO: there is definitely a better way to do this
        storage = WebsocketStorage()
        web_app['websocket_storage'] = storage
        setattr(proxy_server, 'websocket_storage', storage)

        setattr(proxy_server, 'websocket_request_timeout', args.timeout if args.timeout != 0.0 else None)
        setattr(proxy_server, 'websocket_add_forward_headers', [s.strip().lower() for s in (['content-type'] + args.forward_headers)])

        # start both servers
        await self.start_runner(
            web.AppRunner(
                web_app,
                **web_logger_params
            ),
            args.web_host,
            args.web_port,
            'web server'
        )

        await self.start_runner(
            web.ServerRunner(proxy_server),
            args.proxy_host,
            args.proxy_port,
            'proxy server'
        )
