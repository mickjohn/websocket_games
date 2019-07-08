from websocketgames import code_generator
from websocketgames.deck import Deck
from enum import Enum, auto
import logging
import uuid
import json
from collections import defaultdict
from itertools import groupby

logger = logging.getLogger(__name__)

class RedOrBlack():

    MESSAGE_TYPES = [
        'AddPlayer',
        'CreateGame',
    ]

    def __init__(self):
        self.games = {}
        name = type(self).__name__
        self.name = name
        if name not in code_generator.GAME_MODULUS_TABLE:
            raise Exception(f"{name} not registered in GAME_MODULUS_TABLE")

    async def validate_message(self, websocket, message):
        
        pass

    async def handle_close(self, websocket):
        for game in self.games.values():
            if websocket in game.players_ws:
                await game.inactive_player(websocket)
                break

    def inactive_player(self, game, websocket):
        p = game.players_ws[websocket]
        p.active = False
        logger.debug(
            f"Connection lost to {p.username}, marking player inactive")
        logger.debug(f"players = {game.players}")
        del(game.players_ws[websocket])

    async def handle_message(self, message, websocket):
        logger.debug("Red or black handler handling message")
        game_code = message.game_code

        if 'type' in message.data and message.data['type'] == 'CreateGame':
            game_code = code_generator.generate_code(self.name)
            self.games[game_code] = RedOrBlackGame(game_code)
            logger.info(f"Created new game {game_code}")
            await send_game_created(websocket, game_code)
        elif message.game_code not in self.games:
            logger.error(
                f"RedOrBlack Game with code '{game_code}' does not exist")
            await send_error_message(
                websocket,
                'game does not exist',
                f"game with code {game_code} does not exist")
        else:
            game = self.games[message.game_code]
            await game.handle_message(message, websocket)