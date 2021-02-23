from pathlib import Path
from urllib.parse import urljoin
from http import HTTPStatus
from aiohttp import web

from ..websocket_remote import WebsocketRemote


_socket_endpoint = '/ws'


async def _handle_js(request: web.Request):
    req_filename = Path(request.path).name
    # TODO: this part can probably be improved
    js_path = (Path(__file__) / '..' / '..' / 'js' / req_filename).resolve()
    if not js_path.is_file():
        return web.Response(status=HTTPStatus.NOT_FOUND)

    sock_url = urljoin(f'ws://{request.host}', _socket_endpoint)

    js_text = js_path.read_text()
    js_text = js_text.replace('{{SOCK_URL}}', sock_url)

    return web.Response(
        text=js_text,
        headers={'Content-Type': 'application/javascript'}
    )


async def _handle_websocket(request: web.BaseRequest):
    logger = request.app.logger

    peer = request.transport.get_extra_info("peername")
    logger.info(f'got new websocket connection from {peer[0]}:{peer[1]}')

    ws = web.WebSocketResponse(heartbeat=10, max_msg_size=128 * 1024 * 1024)
    await ws.prepare(request)

    storage = request.app['websocket_storage']
    # close any existing connection
    if storage.get() is not None:
        try:
            await storage.get().close()
        except Exception:
            logger.exception('exception occurred while closing existing websocket:')

    # collect messages from new connection
    storage.set(ws)
    try:
        async for msg in ws:
            try:
                WebsocketRemote.response_callback(msg.data)
            except Exception:
                logger.exception('exception occurred while calling response callback:')
    finally:
        if storage.get() is ws:
            storage.clear()


async def _on_shutdown(app: web.Application):
    ws = app['websocket_storage'].get()
    if ws is not None:
        await ws.close()


def setup_app(app: web.Application):
    app.add_routes([
        web.get('/{x}.js', _handle_js),
        web.get(_socket_endpoint, _handle_websocket)
    ])
    app.on_shutdown.append(_on_shutdown)
