import logging
from aiohttp import web
from typing import Optional


class WebsocketStorage:
    _logger = logging.getLogger(__name__)

    def __init__(self):
        self._current_websocket = None

    def get(self) -> Optional[web.WebSocketResponse]:
        return self._current_websocket

    def set(self, websocket: web.WebSocketResponse):
        self._current_websocket = websocket
        self._logger.debug(f'stored new websocket: {websocket}')

    def clear(self):
        self._current_websocket = None
        self._logger.debug('cleared stored websocket')
