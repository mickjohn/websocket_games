import json
import logging
# import asyncio
import jsonpickle

# from websocketgames.games.red_or_black.handler import RedOrBlack
from websocketgames.games.red_or_black.handler import RedOrBlack
from websocketgames.games.high_or_low.handler import HighOrLow
from websocketgames import code_generator

logger = logging.getLogger('websocketgames')


async def game_not_found(game_id, websocket):
    msg = {
        'type': 'Error',
        'error_type': 'GameNotFound',
        'msg': f'Game with id {game_id} not found',
    }
    await websocket.send(jsonpickle.encode(msg, unpicklable=False))


class WebsocketServer():

    def __init__(self):
        self.games = {}
        self.game_constructors = {
            'RedOrBlack': RedOrBlack,
            'HighOrLow': HighOrLow,
        }

    def remove_game(self, game_id):
        if game_id in self.games:
            logger.info(f"removing game {game_id}")
            del(self.games[game_id])

    async def handle_message(self, websocket, path):
        logger.debug(f'path = {path}')
        game_type = path.replace('/', '', 1)
        logger.debug(f'Using "{game_type}" handler to handle message')

        game_id = "not set"
        if path.startswith('/game_'):
            game_id = path.replace('/game_', '')

        try:
            async for message in websocket:
                try:
                    logger.debug(f"message = {message}")
                    data = json.loads(message)
                except json.decoder.JSONDecodeError:
                    await websocket.send(str({'type': 'Error', 'message': 'Invalid JSON'}))
                    raise Exception('Invalid JSON')

                if data['type'] == 'CreateGame':
                    await self.create_game(data, game_type, websocket)
                else:
                    if game_id not in self.games:
                        await game_not_found(game_id, websocket)
                        await websocket.close()
                    else:
                        game = self.games[game_id]
                        await game.handle_message(data, websocket)

        except Exception as e:
            logger.error(str(e))

        finally:
            if game_id in self.games:
                await self.games[game_id].handle_close(websocket)
            logger.debug('Closing websocket connection')

    async def create_game(self, data, gametype, websocket):
        game_code = code_generator.generate_code(gametype)
        game = self.game_constructors[gametype]
        self.games[game_code] = game(
            game_code,
            cleanup_handler=self.remove_game,
            options=data.get('options', {})
        )
        logger.info(f"Created new {gametype} game {game_code}")
        msg = {
            'type': 'GameCreated',
            'game_code': game_code
        }
        await websocket.send(jsonpickle.encode(msg, unpicklable=False))
