import json
import logging
# import asyncio
import jsonpickle

# from websocketgames.games.red_or_black.handler import RedOrBlack
from websocketgames.games.red_or_black.handler2 import RedOrBlack
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
            'RedOrBlack': RedOrBlack
        }

    # async def cleanup_loop(self):
    #     logger.info("Server cleanup loop starting")
    #     while(True):
    #         for handler in list(self.game_handlers.values()):
    #             await handler.run_cleanup()
    #         await asyncio.sleep(5)

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
                    data = json.loads(message)
                except json.decoder.JSONDecodeError:
                    raise Exception('Invalid JSON')

                if data['type'] == 'CreateGame':
                    await self.create_game(data, game_type, websocket)
                else:
                    if game_id not in self.games:
                        await game_not_found(game_id, websocket)
                        websocket.close()
                    else:
                        game = self.games[game_id]
                        await game.handle_message(data, websocket)

        except Exception as e:
            logger.error(str(e))

        finally:
            if game_id in self.games:
                await self.games[game_id].handle_close(websocket)
            # await self.game_handlers[game_type].handle_close(websocket)
            logger.debug('Closing websocket connection')

    async def create_game(self, data, gametype, websocket):
        game_code = code_generator.generate_code(gametype)
        game = self.game_constructors[gametype]
        self.games[game_code] = game(game_code)
        logger.info(f"Created new {gametype} game {game_code}")
        msg = {
            'type': 'GameCreated',
            'game_code': game_code
        }
        await websocket.send(jsonpickle.encode(msg, unpicklable=False))
