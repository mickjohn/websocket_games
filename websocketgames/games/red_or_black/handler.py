from websocketgames import code_generator
from websocketgames.games.red_or_black.game import RedOrBlackGame
from collections import defaultdict
import logging
import json

logger = logging.getLogger('websocketgames')

MESSAGE_TYPES = [
    'AddPlayer',
    'CreateGame',
]


class Message():
    '''
    A class that represents a incoming message that is sent from a client. It
    is initialised by passing a json dict that is created by deserialising the
    incoming data from the client. The json dict is then validated and if it's
    OK then the message is initialised, containing the game_id and data
    '''
    def __init__(self, json_dict):
        if 'game_id' not in json_dict:
            raise Exception("Field 'game_id' is missing")
        if 'data' not in json_dict:
            raise Exception("Field 'data' is missing")
        if 'type' not in json_dict:
            raise Exception("Field 'type' is missing")

        if not isinstance(json_dict['data'], dict):
            raise Exception('data should be an object')

        if json_dict['type'] not in MESSAGE_TYPES:
            raise Exception(f"Unknown message type '{json_dict['type']}''")

        self.game_id = json_dict['game_id']
        self.data = json_dict['data']
        self.type = json_dict['type']


async def send_message(websocket, **kwargs):
    await websocket.send(str(kwargs))


class RedOrBlack():

    def __init__(self):
        self.games = {}
        self.players = defaultdict(dict)
        name = type(self).__name__
        self.name = name
        if name not in code_generator.GAME_MODULUS_TABLE:
            raise Exception(f"{name} not registered in GAME_MODULUS_TABLE")

    # async def handle_close(self, websocket):
    #     for game in self.games.values():
    #         if websocket in game.players_ws:
    #             await game.inactive_player(websocket)
    #             break

    # def inactive_player(self, game, websocket):
    #     p = game.players_ws[websocket]
    #     p.active = False
    #     logger.debug(
    #         f"Connection lost to {p.username}, marking player inactive")
    #     logger.debug(f"players = {game.players}")
    #     del(game.players_ws[websocket])

    async def handle_message(self, json_dict, websocket):
        logger.debug("RedOrBlack handler handling message")
        message = Message(json_dict)

        if message.type == 'CreateGame':
            game_code = self.create_game()
            await send_message(websocket, type='GameCreated', game_code=game_code)
            return
        
        if message.game_id not in self.games:
            logger.error(f"Game with code '{game_code}' does not exist")
            error_msg = {
                'type': 'Error',
                'error': f"no RedOrBlack game with code {game_code} exists"
            }
            send_message(websocket, *error_msg)
        
        # if 'type' in message.data and message.data['type'] == 'CreateGame':
        #     game_code = code_generator.generate_code(self.name)
        #     self.games[game_code] = RedOrBlackGame(game_code)
        #     logger.info(f"Created new game {game_code}")
        #     await send_game_created(websocket, game_code)
        # elif message.game_code not in self.games:
        #     logger.error(
        #         f"RedOrBlack Game with code '{game_code}' does not exist")
        #     await send_error_message(
        #         websocket,
        #         'game does not exist',
        #         f"game with code {game_code} does not exist")
        # else:
        #     game = self.games[message.game_code]
        #     await game.handle_message(message, websocket)

    def create_game(self):
        game_code = code_generator.generate_code(self.name)
        self.games[game_code] = RedOrBlackGame(game_code)
        logger.info(f"Created new game {game_code}")
        return game_code
