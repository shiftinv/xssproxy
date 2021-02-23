import json
import logging
import asyncio
import base64
from aiohttp import web
from typing import Dict, List, Tuple, Optional


class WebsocketRemote:
    __seq = 0  # not sure if this is thread safe
    __events = {}
    __responses = {}

    _logger = logging.getLogger(__name__)

    @classmethod
    async def http_request(cls, websocket: web.WebSocketResponse, timeout: Optional[float], method: str, url: str, headers: List[Tuple[str, str]], body: bytes):
        seq = cls.__seq
        cls.__seq += 1

        cls._logger.debug(f'sending request with seq {seq} for {url} ({method}, headers: {len(headers)}, size: {len(body)})')
        response = await cls.__send_and_wait(
            websocket,
            timeout,
            seq,
            {
                'method': method,
                'url': url,
                'headers': headers,
                'body': base64.b64encode(body).decode()  # not the most efficient encoding ('latin-1' could work as well), but it'll do for now
            }
        )

        if 'error' in response:
            return response

        keys = set(response.keys())
        if keys != {'status', 'headers', 'body'}:
            raise RuntimeError(f'unexpected keys in response: {keys}')

        response['body'] = base64.b64decode(response['body'])
        return response

    @classmethod
    def response_callback(cls, response: str):
        try:
            obj = json.loads(response)
        except json.JSONDecodeError as e:
            raise RuntimeError(f'received invalid json: {response}') from e

        if 'seq' not in obj:
            raise RuntimeError(f'no seq in received response. keys: {set(obj.keys())}')
        seq = obj.pop('seq')

        if seq not in cls.__events:
            raise RuntimeError(f'no event found for seq {seq}')

        cls.__responses[seq] = obj
        cls.__events[seq].set()

    @classmethod
    async def __send_and_wait(cls, websocket: web.WebSocketResponse, timeout: Optional[float], seq: int, obj: Dict):
        # TODO: use futures instead of events
        evt = asyncio.Event()
        cls.__events[seq] = evt

        await websocket.send_json({
            'seq': seq,
            **obj
        })

        cls._logger.debug(f'waiting for response for seq {seq}')

        try:
            await asyncio.wait_for(evt.wait(), timeout)
        except asyncio.TimeoutError:
            cls._logger.error(f'request for seq {seq} timed out')
            raise
        del cls.__events[seq]

        if seq not in cls.__responses:  # this *should* never happen, but it's still handled just to be sure
            raise RuntimeError(f'event for seq {seq} was set, but no matching response exists')
        cls._logger.debug(f'got response for seq {seq}')
        return cls.__responses.pop(seq)
