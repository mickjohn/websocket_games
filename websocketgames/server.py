import json
import logging

from websocketgames.games.red_or_black.handler import RedOrBlack

logger = logging.getLogger('websocketgames')

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
            'redorblack': RedOrBlack(run_cleanup_thead=True)
        }

    async def handle_message(self, websocket, path):
        logger.debug(f'path = {path}')
        game_type = path.replace('/', '', 1)
        logger.debug(f'Using "{game_type}" handler to handle message')

        try:
            handler = self.game_handlers[game_type]
        except KeyError:
            raise Exception(f"There is no handler for '{game_type}'")

        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                except json.decoder.JSONDecodeError:
                    raise Exception('Invalid JSON')

                await handler.handle_message(data, websocket)

        except Exception as e:
            logger.error(str(e))

        finally:
            await self.game_handlers[game_type].handle_close(websocket)
            # await websocket.close()
            logger.debug('Closing websocket connection')
