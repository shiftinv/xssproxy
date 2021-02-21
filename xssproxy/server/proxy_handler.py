from aiohttp import web

from ..websocket_remote import WebsocketRemote


async def handler(request: web.BaseRequest):
    websocket = getattr(request.protocol._manager, 'websocket_storage').get()
    if websocket is None:
        return web.Response(status=418, text='no websocket connected')

    remote_response = await WebsocketRemote.http_request(
        websocket,
        request.method,
        request.raw_path,  # .path_qs?
        dict(request.headers),
        await request.read()
    )

    return web.Response(
        status=remote_response['status'],
        headers=remote_response['headers'],
        body=remote_response['body']
    )


def setup_server(server: web.Server):
    server.request_handler = handler
