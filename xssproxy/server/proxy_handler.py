import asyncio
from aiohttp import web

from ..websocket_remote import WebsocketRemote


async def handler(request: web.BaseRequest):
    logger = request.protocol.logger

    websocket = request.protocol._manager.websocket_storage.get()
    if websocket is None:
        return web.Response(status=553, text='no websocket connected')

    if not request.raw_path.startswith('http://'):
        return web.Response(status=554, text='invalid url')

    # drop 'User-Agent' header
    headers = [(k, v) for k, v in request.headers.items() if k.lower() != 'user-agent']

    # send request through websocket
    try:
        remote_response = await WebsocketRemote.http_request(
            websocket,
            request.protocol._manager.websocket_request_timeout,
            request.method,
            request.raw_path,
            headers,
            await request.read()
        )
    except asyncio.TimeoutError:
        return web.Response(
            status=556,
            text='request timed out'
        )

    if 'error' in remote_response:
        err = remote_response['error']
        logger.error(f'received error: {err}')
        return web.Response(
            status=555,
            text=f'request failed (error: {err})'
        )
    else:
        # remove content length (some web servers report inaccurate values for some reason)
        remote_response['headers'] = [h for h in remote_response['headers'] if h[0].lower() != 'content-length']
        return web.Response(
            status=remote_response['status'],
            headers=remote_response['headers'],
            body=remote_response['body']
        )


def setup_server(server: web.Server):
    server.request_handler = handler
