# WS server example that synchronizes state across clients

import asyncio
import json
import logging
import websockets

from websocketgames.games.red_or_black import RedOrBlack

logger = logging.getLogger('root')

'''
incoming message format
{
    'game_id': 'aaaa',
    'game_type': 'RedOrBlack',
    'data': {...}
}
'''


class Message():
    def __init__(self, game_code, game_type, data):
        self.game_code = game_code
        self.game_type = game_type
        self.data = data


class WebsocketServer():

    def __init__(self):
        self.game_handlers = {
            'redorblack': RedOrBlack()
        }

    async def handle_message(self, websocket, path):
        logger.debug(f'path = {path}')
        game_type = path.replace('/', '', 1)
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                except json.decoder.JSONDecodeError:
                    logger.error(f'Invalid JSON')

                try:
                    message = Message(data['game_id'], game_type, data['data'])
                except KeyError:
                    logger.error(f'invalid message format: {data}')

                try:
                    handler = self.game_handlers[message.game_type]
                    await handler.handle_message(message, websocket)
                except KeyError:
                    logger.error(
                        f"There is no handler for '{message.game_type}'")

        finally:
            await self.game_handlers[game_type].handle_close(websocket)
            logger.debug('Closing websocket connection')
