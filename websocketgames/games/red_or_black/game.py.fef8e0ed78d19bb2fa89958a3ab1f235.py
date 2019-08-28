import jsonpickle
from enum import Enum
from websocketgames.deck import Deck
from enum import Enum, auto
import logging
import uuid
from collections import defaultdict
from itertools import groupby

logger = logging.getLogger(__name__)


class JsonEnumHandler(jsonpickle.handlers.BaseHandler):

    def restore(self, obj):
        pass

    def flatten(self, obj: Enum, data):
        return obj.name


class Player():

    def __init__(self, username, user_id, active=True):
        self.username = username
        self.user_id = user_id
        self.active = active

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.__dict__ == other.__dict__
        return False


class GameStates(Enum):
    LOBBY = auto()
    PLAYING = auto()
    FINISHED = auto()

    def __str__(self):
        if self == self.LOBBY:
            return 'LOBBY'
        elif self == self.PLAYING:
            return 'PLAYING'
        elif self.FINISHED:
            return 'FINISHED'
        return ''

    def __repr__(self):
        return str(self)


# Use custom JSON handler for GameStates
jsonpickle.handlers.registry.register(GameStates, JsonEnumHandler)


class RedOrBlackGame():
    '''
    The 'owner' is the first person to join the game. The client should be
    implemented in a way that ensures that the creator of the game is the
    first person to join. The owner is the only player who can start and
    restart the game.
    '''

    def __init__(self, game_code):
        self.game_code = game_code
        # Map of username -> Player
        self.registered_players = {}

        # Map of id -> Player
        self.registered_ids = {}

        # Map of username -> Player
        self.usernames_map = {}

        # Map of user id -> Player
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

    def get_full_game_state(self):
        state = {
            'players': list(self.usernames_map.values()),
            'turn': self.turn,
            'state': str(self.state),
            'owner': self.owner,
            'order': self.order,
        }
        return state

    def add_player_by_username(self, username):
        '''
        Add a player into the game by username. If the username is taken an
        exception is thrown. A UUID is created and a Player object is returned.
        The player is added to the internal structures of the game.
        This is the same as registering a player and activating the player.
        '''
        if username in self.usernames_map or username in self.registered_players:
            logger.error(f"User {username} already exists in {self.game_code}")
            raise UserAlreadyExists(
                f"User {username} already exists in {self.game_code}")

        user_id = str(uuid.uuid4())
        logger.info(f"Adding player {username} to game {self.game_code}")
        player = Player(username, user_id)
        self.usernames_map[player.username] = player
        self.id_map[user_id] = player
        self.order.append(player)
        if self.owner is None:
            self.owner = player
        return user_id

    def activate_player(self, user_id):
        '''
        Activate a registered player
        '''
        if user_id not in self.registered_ids:
            err_msg = f"ID {user_id} not found in registered users"
            logger.error(err_msg)
            raise(UserDoesNotExist(err_msg))

        if user_id in self.id_map:
            logger.info(
                f'id "{user_id}" already activated, not doing anything')
            return

        player = self.registered_ids[user_id]
        player.active = True
        logger.info(
            f"Adding player {player.username} to game {self.game_code}")
        self.usernames_map[player.username] = player
        self.id_map[user_id] = player
        self.order.append(player)
        if self.owner is None:
            self.owner = player

    def register_player(self, username):
        '''
        Create a player, but don't add to the game. 'activate_player' must be
        called afterwards to enable the player.
        '''
        if username in self.registered_players or username in self.usernames_map:
            err_msg = f"User {username} already registered in {self.game_code}"
            logger.error(err_msg)
            raise UserAlreadyExists(err_msg)
        user_id = str(uuid.uuid4())
        logger.info(f"Registering player {username} in game {self.game_code}")
        player = Player(username, user_id)
        player.active = False
        self.registered_players[username] = player
        self.registered_ids[user_id] = player
        return player

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

    def _get_current_player(self):
        if len(self.usernames_map) == 0:
            return None
        index = self.turn % len(self.order)
        current_player = self.order[index]
        return current_player
        

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
        return_messages = []
        if user_id in self.id_map:
            p = self.id_map[user_id]
            logger.debug(f'Removing player {p.username}')
            return_messages.append({
                'type': 'PlayerLeft',
                'player': p
            })
            del(self.id_map[user_id])
            del(self.usernames_map[p.username])
            if not len(self.id_map):
                logger.debug('Ending game due to lack of players')
                self.end_game()
            elif p in self.order:
                index = self.order.index(p)
                del(self.order[index])
        return return_messages

    def make_player_inactive(self, user_id):
        return_messages = []
        if user_id in self.id_map:
            player = self.id_map[user_id]
            logger.debug(f'making player {player.username} inactive')
            player.active = False
            return_messages.append({
                'type': 'PlayerDisconnected',
                'player': player
            })

            if len(self.id_map) == 1:
                logger.debug(f"'{player.username}' is the last player in the"
                             "game. Stopping the game")
                self.end_game()
                return_messages.append({'type': 'GameStopped'})

            # Get the current player to check if it's the player that has
            # become inactive
            current_active_player = self._get_current_player()

            # Remove the inactive player from the game order
            index = self.order.index(player)
            del(self.order[index])

            if current_active_player == player and self.is_playing():
                logger.debug(
                    f'Current player is becoming inactive, changing player')
                next_active_player = self._get_current_player()
                return_messages.append({
                    'type': 'PlayerTurnChanged',
                    'player': next_active_player
                })

        return return_messages

    def reactivate_player(self, user_id):
        return_messages = []
        if user_id in self.id_map:
            p = self.id_map[user_id]
            if not p.active:
                p.active = True
                self.order.append(p)
                logger.info(f"Reactivated user {p.username}")
                return_messages.append({
                    'type': 'PlayerRejoined',
                    'player': p,
                })
            else:
                logger.error(
                    f"User {p.username} is already active, not doing anything")
        else:
            logger.error(f"id {user_id} not in this game")
        return return_messages

    def _get_ranks(self, usernames):
        '''
        given a dict of usernames this will return a list of tuples:
        [('score', 'usernames with that score')]
        '''
        score_dict = defaultdict(list)

        # Add all of the games users to the list
        # Then subtract their score by 1, poeple with 0
        # simply didn't score.
        usernames = sorted(usernames + list(self.usernames_map.keys()))

        # Build dict of {'occurences': [names]}
        for username, occurences in groupby(usernames):
            score = len(list(occurences)) - 1
            score_dict[score].append(username)

        # Sort the keys
        scores = sorted(score_dict.keys())

        # Build list of tuples
        score_list = [(score, score_dict[score]) for score in scores]
        return score_list

    def present_stats(self):
        outcomes = self.stats['outcomes']
        turns = len(outcomes)
        pretty_stats = {}
        pretty_stats['turns'] = turns
        right = []
        red_guesses = 0
        for __turn, outcome in outcomes.items():
            # List of usernames that got their turn right/wrong
            if outcome['outcome']:
                right.append(outcome['player'].username)

            # Counter of how many guesses were red
            if outcome['guess'] == 'Red':
                red_guesses += 1

        pretty_stats['right_guesses'] = len(right)
        pretty_stats['wrong_guesses'] = turns - len(right)
        pretty_stats['red'] = red_guesses
        pretty_stats['black'] = turns - red_guesses
        pretty_stats['scores'] = self._get_ranks(right)
        return pretty_stats


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
