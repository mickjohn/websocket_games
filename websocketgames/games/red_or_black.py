from websocketgames import code_generator
from websocketgames.deck import Deck
from enum import Enum, auto
import logging
import uuid
from sched import scheduler

logger = logging.getLogger('root')


def send_game_created(websocket, game_code):
    return websocket.send(str({
        'type': 'GameCreated',
        'code': game_code,
    }))


def send_error_message(websocket, summary, desc=''):
    return websocket.send(str({
        'type': 'Error',
        'summary': summary,
        'description': desc,
    }))


class Player():

    def __init__(self, username, user_id, active=True):
        self.username = username
        self.user_id = user_id
        self.active = active

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)


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


class GameStates(Enum):
    LOBBY = auto()
    PLAYING = auto()
    FINISHED = auto()


class RedOrBlackGame():
    '''
    The 'owner' is the first person to join the game. The client should be 
    implemented in a way that ensures that the creator of the game is the 
    first person to join. The owner is the only player who can start and
    restart the game.
    '''

    def __init__(self, game_code):
        self.game_code = game_code
        self.usernames_map = {}
        self.id_map = {}
        self.turn = 0
        self.state = GameStates.LOBBY
        self.owner = None
        self.order = []
        self.deck = Deck(shuffled=True)
        self.stats = {
            'outcomes': {}
        }

    def is_lobby(self):
        return self.state == GameStates.LOBBY

    def is_playing(self):
        return self.state == GameStates.PLAYING

    def is_finished(self):
        return self.state == GameStates.FINISHED

    def add_player(self, username):
        if username in self.usernames_map:
            logger.error(f"User {username} already exists in {self.game_code}")
            raise UserAlreadyExists(
                f"User {username} already exists in {self.game_code}")

        user_id = str(uuid.uuid4())
        logger.info(f"Adding player {username} to game {self.game_code}")
        player = Player(username, user_id)
        self.usernames_map[player.username] = player
        self.id_map[user_id] = player
        self.order.append(player)
        if self.owner == None:
            self.owner = player
        return user_id

    def start_game(self, user_id):
        if user_id not in self.id_map:
            raise UserDoesNotExist(f"No id {user_id} in game {self.game_code}")

        player = self.id_map[user_id]
        if self.owner != player:
            raise UserNotAllowedToStart(
                f"User {player.username} is not allowed to start the game")

        self.state = GameStates.PLAYING

    def draw_card(self):
        return self.deck.draw_card()

    def get_card_colour(self, card):
        if card.suit == 'Spades' or card.suit == 'Clubs':
            return 'Black'
        else:
            return 'Red'

    def can_play_turn(self, user_id):
        if not self.is_playing():
            logger.error("Game is not in playing state")
            raise WrongStateException("Game is not in playing state")

        index = self.turn % len(self.order)
        current_player = self.order[index]
        player = self.id_map[user_id]
        if user_id != current_player.user_id:
            logger.error(
                f"It's not the go of {player.username}, it's {current_player.username}")
            raise NotPlayersTurn(
                f"It's not the go of {player.username}, it's {current_player.username}")

        return True

    def play_turn(self, user_id, guess):
        self.can_play_turn(user_id)
        player = self.id_map[user_id]
        card = self.deck.draw_card()
        colour = self.get_card_colour(card)
        correct = guess == colour

        self.turn += 1

        self.stats['outcomes'][self.turn] = {
            'player': player,
            'turn': self.turn,
            'guess': guess,
            'outcome': correct,
            'card': card,
        }

        if len(self.deck.cards) == 0:
            self.end_game()

        return correct

    def end_game(self):
        self.state = GameStates.FINISHED

    def restart_game(self, user_id):
        self.state = GameStates.PLAYING
        self.turn = 0
        self.deck = Deck(shuffled=True)
        self.stats = {
            'outcomes': {}
        }
        self.start_game(user_id)

    def remove_player(self, user_id):
        if user_id in self.id_map[user_id]:
            p = self.id_map[user_id]
            del(self.id_map[user_id])
            del(self.usernames_map[p.username])
            if p in self.order:
                index = self.order.index(p)
                del(self.order[index])


class UserAlreadyExists(Exception):
    pass


class NotPlayersTurn(Exception):
    pass


class UserDoesNotExist(Exception):
    pass


class UserNotAllowedToStart(Exception):
    pass


class WrongStateException(Exception):
    pass
