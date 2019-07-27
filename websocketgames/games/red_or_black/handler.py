from websocketgames import code_generator
from websocketgames.games.red_or_black.game import RedOrBlackGame, UserAlreadyExists
from collections import defaultdict
import logging
from threading import Thread, Lock
import time
import json
import jsonpickle

logger = logging.getLogger('websocketgames')

MESSAGE_TYPES = [
    'AddPlayer',
    'CreateGame',
    'ReaddPlayer',
]

SENDABLE_MESSAGES = [
    'Error',
    'PlayerAdded',
    'GameCreated',
    'Debug',
]

INTERNAL_MESSAGES = [
    'PlayerRejoined',
    'PlayerLeft',
    'PlayerTurnChanged',
    'GameStopped',
    'PlayerDisconnected',
]

SENDABLE_MESSAGES = SENDABLE_MESSAGES + INTERNAL_MESSAGES

MAX_INACTIVE_TIME = 10
THREAD_PAUSE_TIME = 5


class Client():
    '''
    A class containing a user id, game id & websocket connection
    '''

    def __init__(self, user_id, game_id, websocket):
        self.user_id = user_id
        self.game_id = game_id
        self.websocket = websocket


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


async def send_message(websocket, msg_type, **kwargs):
    if msg_type not in SENDABLE_MESSAGES:
        raise Exception(f"Message type '{msg_type}' is unkown."
                        "Known message types are {SENDABLE_MESSAGES}")
    msg = {
        'type': msg_type,
        **kwargs
    }
    json_msg = jsonpickle.encode(msg, unpicklable=False)
    await websocket.send(json_msg)


async def broadcast_message(websockets, msg_type, **kwargs):
    for websocket in websockets:
        if websocket.open:
            await send_message(websocket, msg_type, **kwargs)


class RedOrBlack():

    def __init__(self, run_cleanup_thead=False):
        # Map of 'game id -> game'
        self.games = {}

        # Map of 'player_id -> (websocket, game_id)'
        self.players_id = {}

        # Map of 'websocket -> (user id, game_id)
        self.players_websocket = {}

        # Mapf of user_id -> Client
        self.clients = {}

        # Set of players that have disconnected
        self.inactive_player_ids = set()

        # Map of 'player id -> num of seconds inactive
        self.inactive_player_counter = defaultdict(int)

        # Mutex for controlling access to some resources that can be modified
        # by more than one thread
        self.mutex = Lock()

        name = type(self).__name__
        self.name = name
        if name not in code_generator.GAME_MODULUS_TABLE:
            raise Exception(f"{name} not registered in GAME_MODULUS_TABLE")

        # Start cleanup thread
        if run_cleanup_thead:
            cleanup_thread = Thread(
                target=self._player_cleanup_thread, args=())
            cleanup_thread.start()

    def _get_websockets_for_game(self, game_id):
        websockets = []
        for websocket, gid in list(self.players_id.values()):
            if gid == game_id:
                logger.debug(f'adding websocket to websockets')
                websockets.append(websocket)
        logger.debug(f'brdcst skts = {websockets}')
        return websockets

    async def handle_close(self, websocket):
        if websocket not in self.players_websocket:
            return
        logger.debug("Handling websocket disconnection")
        # Check if player is in game
        (user_id, game_id) = self.players_websocket[websocket]
        if user_id and game_id:
            game = self.games[game_id]
            logger.debug(f"Adding {user_id} to inactive IDs")
            self.inactive_player_ids.add(user_id)
            resp = game.make_player_inactive(user_id)
            broadcast_sockets = self._get_websockets_for_game(game_id)
            for msg in resp:
                await broadcast_message(
                    broadcast_sockets,
                    msg['type'],
                    **msg,
                )

    async def handle_message(self, json_dict, websocket):
        logger.debug("RedOrBlack handler handling message")
        message = Message(json_dict)
        game_id = message.game_id

        if message.type == 'CreateGame':
            game_code = self._create_game()
            await send_message(websocket, 'GameCreated', game_code=game_code)
            return

        if game_id not in self.games:
            logger.error(f"Game with code '{game_id}' does not exist")
            error_msg = {
                'error': f"no RedOrBlack game with code {game_id} exists"
            }
            await send_message(websocket, 'Error', **error_msg)
            return

        if message.type == 'AddPlayer':
            username = message.data['username']
            try:
                player = self._add_player(username, game_id, websocket)
                await send_message(websocket, 'PlayerAdded', player=player)
            except UserAlreadyExists:
                await send_message(websocket,
                                   'Error', error=f"User with name {username} already exists in game")

    def _create_game(self):
        game_code = code_generator.generate_code(self.name)
        self.games[game_code] = RedOrBlackGame(game_code)
        logger.info(f"Created new game {game_code}")
        return game_code

    def _add_player(self, username, game_id, websocket):
        game = self.games[game_id]
        self.mutex.acquire()
        user_id = game.add_player(username)
        player = game.id_map[user_id]
        self.players_id[user_id] = (websocket, game_id)
        self.players_websocket[websocket] = (user_id, game_id)
        client = Client(user_id, game_id, websocket)
        self.clients[user_id] = client
        self.mutex.release()
        return player

    '''
    Should be run in a thread
    '''

    def _player_cleanup_thread(self):
        logger.info("Starting up RedOrBlack handler cleanup thread")
        while True:
            self.mutex.acquire()
            for player_id in self.inactive_player_ids:
                if player_id not in self.players_id:
                    logger.debug(f"{player_id} has rejoined!")
                    self.inactive_player_counter[player_id] = 0
                else:
                    self.inactive_player_counter[player_id] += THREAD_PAUSE_TIME

            # Keep track of players that have been removed from games, so that
            # we can remove all traces of them after they have disconnected
            # and timed out.
            removed_ids = []
            for player_id, inactive_time in self.inactive_player_counter.items():
                if inactive_time >= MAX_INACTIVE_TIME:
                    # Remove player from their game
                    (__websocket, game_id) = self.players_id[player_id]
                    if game_id:
                        game = self.games[game_id]
                        player = game.id_map[player_id]
                        logger.info(
                            f"Removing {player.username} from game due to inactivity")
                        game.remove_player(player_id)
                        del(self.clients[player_id])
                        removed_ids.append(player_id)

            # Clean up the counter dict
            for player_id in removed_ids:
                self.inactive_player_ids.remove(player_id)
                del(self.inactive_player_counter[player_id])

            self.mutex.release()
            time.sleep(THREAD_PAUSE_TIME)
