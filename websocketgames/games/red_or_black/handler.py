import jsonpickle
import logging
import asyncio
from enum import auto, Enum

from websocketgames.deck import Deck
from websocketgames.games.red_or_black import validator
from websocketgames.games.red_or_black import utils
from websocketgames.games.red_or_black.errors import *
from websocketgames.games.red_or_black.clients import Client, ClientRegistery
from websocketgames.games.red_or_black.players import Player, PlayerRegistery

from collections import defaultdict
import uuid

logger = logging.getLogger('websocketgames')


class JsonEnumHandler(jsonpickle.handlers.BaseHandler):

    def restore(self, obj):
        pass

    def flatten(self, obj: Enum, data):
        return obj.name


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


class RedOrBlack:

    def __init__(self, game_code, cleanup_handler=None):
        self.game_code = game_code

        self.p_reg = PlayerRegistery()
        self.c_reg = ClientRegistery()

        self.turn = 0
        self.state = GameStates.LOBBY
        self.owner = None
        self.deck = Deck(shuffled=True)
        self.penalty_increment = 1
        self.penalty_start = 1
        self.penalty = 1
        self.stats = {
            'outcomes': []
        }

        self.cleanup_handler = cleanup_handler

        # Set of players that have disconnected
        self.inactive_player_ids = set()

        # Map of 'player id -> num of seconds inactive
        self.inactive_player_counter = defaultdict(int)

    def __repr__(self):
        return (
            f"\n[{self.game_code}]: registered_players: {self.p_reg}\n"
            f"[{self.game_code}]: turn: {self.turn}\n"
            f"[{self.game_code}]: state: {self.state}\n"
            f"[{self.game_code}]: owner: {self.owner}\n"
            f"[{self.game_code}]: order: {self.p_reg.get_order()}\n"
            f"[{self.game_code}]: cards left: {len(self.deck.cards)}\n"
            f"[{self.game_code}]: player registery: {self.p_reg}\n"
            f"[{self.game_code}]: client registery: {self.c_reg}\n"
        )

    def _debug(self):
        logger.debug(self)

    async def handle_message(self, json_dict, websocket):
        if json_dict['type'] == 'Debug':
            self._debug()
            return
        validator.validate_msg(json_dict)
        message = json_dict
        msg_type = json_dict['type']

        if msg_type == 'Register':
            await self.register_player(websocket, message)
        elif msg_type == 'Activate':
            await self.activate_player(websocket, message)
        elif msg_type == 'StartGame':
            await self.start_game(websocket, message)
        elif msg_type == 'PlayTurn':
            await self.play_turn(websocket, message)

    async def register_player(self, websocket, msg):
        '''
        Create a player, but don't add to the game. 'activate_player' must be
        called afterwards to enable the player. This does not add a new client
        '''
        username = msg['username']
        new_player = Player(username, str(uuid.uuid4()), False)

        if self.p_reg.uname_exists(username):
            err_msg = f"User {username} already registered in {self.game_code}"
            logger.error(err_msg)
            await utils.send_message(
                websocket,
                'Error',
                error_type="UserAlreadyRegistered",
                error=f"User with name {username} already registered in game"
            )
            return None

        logger.info(f"Registering player {username} in game {self.game_code}")
        self.p_reg.add_player(new_player)
        await utils.send_message(websocket, 'Registered', user_id=new_player.user_id)
        return new_player

    async def activate_player(self, websocket, msg):
        '''
        Activate a registered Player
        '''
        user_id = msg['user_id']
        if user_id not in self.p_reg.id_map:
            await utils.send_message(
                websocket,
                'Error',
                error=f"User with id {user_id} does not exist in game {self.game_code}"
            )
            return None

        logger.info(f"Activating player {user_id} in game {self.game_code}")

        if user_id in self.inactive_player_ids:
            self.inactive_player_ids.remove(user_id)

        player = self.p_reg.id_map[user_id]
        player.active = True

        if self.owner == None:
            self.owner = player

        self.c_reg.connect(websocket, player)

        await utils.broadcast_message(
            self.c_reg.websockets(),
            'PlayerAdded',
            player=player,
            skip=[websocket]
        )

        await utils.broadcast_message(
            self.c_reg.websockets(),
            'OrderChanged',
            order=self.p_reg.get_order()
        )

        await utils.send_message(
            websocket,
            'YouJoined',
            player=player,
            game_state=self.get_full_game_state(),
        )

        return player

    async def handle_close(self, websocket):
        '''
        Handle the close of a websocket of an active client, and send out
        messages of the new state. The playing order will change, the owner
        could change.
        '''
        if websocket not in self.c_reg.clients:
            return
        logger.debug("Handling websocket disconnection")
        client = self.c_reg.clients[websocket]
        if client and client.player:
            player = client.player
            self.p_reg.deactivate(player)
            # self.inactive_player_ids.add(player.user_id)
            self.c_reg.remove(websocket)
            resp = []

            # Send msg that player has disconnected
            resp.append({
                'type': 'PlayerDisconnected',
                'player': player,
            })

            if self.owner.user_id == player.user_id:
                if len(self.p_reg.get_order()):
                    new_owner = self.p_reg.get_order()[0]
                else:
                    new_owner = None
                self.owner = new_owner
                # Inform players that there is a new owner
                resp.append({
                    'type': 'NewOwner',
                    'owner': new_owner,
                })

            # The game order will have changed
            resp.append({
                'type': 'OrderChanged',
                'order': self.p_reg.get_order()
            })

            for msg in resp:
                await utils.broadcast_message(
                    self.c_reg.websockets(),
                    msg['type'],
                    **msg,
                )
        websocket.close()

    async def start_game(self, websocket, msg):
        '''
        Start the game. If the user_id is not the ID of the owner, send an
        error. If the game is started, broadcast a message saying the game
        has started.
        '''
        user_id = msg['user_id']
        if user_id not in self.p_reg.id_map:
            await utils.send_message(
                websocket,
                'Error',
                error=f"User with id {user_id} does not exist in game {self.game_code}"
            )
            return

        player = self.p_reg.id_map[user_id]
        if self.owner != player:
            await utils.send_message(
                websocket,
                'Error',
                error=f"User with id {user_id} not allowed to start the game"
            )
            return

        self.state = GameStates.PLAYING
        await utils.broadcast_message(self.c_reg.websockets(), 'GameStarted')

    '''
    Take a players guess and progress the game by one turn, and send the
    outcome to all the players in the game.
    '''
    async def play_turn(self, websocket, msg):
        # Before processing the turn, sleep for some time to add to the suspense
        await asyncio.sleep(1)
        logger.debug('Playing turn')
        if websocket not in self.c_reg.clients:
            await utils.send_user_not_found(websocket)
            return

        if self.c_reg.clients[websocket].player == None:
            await utils.send_user_not_found(websocket)
            return

        player = self.c_reg.clients[websocket].player
        order = self.p_reg.get_order()
        current_player = self.p_reg.get_order()[self.turn % len(order)]
        return_penalty = self.penalty

        if self.state != GameStates.PLAYING:
            logger.error(f"Game is not in playing state")
            await utils.send_message(websocket, 'GameNotStarted')
            return

        if player != current_player:
            logger.error(f"It's not the turn of '{player.username}'")
            await utils.send_message(websocket, 'NotPlayerTurn')
            return

        if not len(self.deck.cards):
            logger.error('No cards left!')
            return

        guess = msg['guess']
        card = self.deck.draw_card()
        correct = guess == card.get_colour()
        logger.info(
            f"guess for {player.username}: card={card} guess={guess} correct={correct}")

        # Update the stats of the game
        self.stats['outcomes'].append({
            'player': player,
            'turn': self.turn,
            'guess': guess,
            'outcome': correct,
            'card': card,
        })
        self.turn += 1

        if correct:
            self.penalty += self.penalty_increment
        else:
            self.penalty = self.penalty_start

        await utils.broadcast_message(
            self.c_reg.websockets(),
            'GuessOutcome',
            correct=correct,
            guess=guess,
            turn=self.turn,
            penalty=return_penalty,
            new_penalty=self.penalty,
            player=player,
            cards_left=len(self.deck.cards),
        )

    '''
    Gather info about the game and place it into a dict. This will be sent to
    a player when they join the game.
    '''
    def get_full_game_state(self):
        state = {
            'players': list(self.p_reg.id_map.values()),
            'turn': self.turn,
            'state': str(self.state),
            'owner': self.owner,
            'order': self.p_reg.get_order(),
            'shortend_history': self.stats['outcomes'][0:10],
        }
        return state

    '''
    Get the player who's turn it is
    '''
    def get_current_player(self):
        if self.state != GameStates.PLAYING:
            return None

        order = self.p_reg.get_order()
        order_len = len(order)
        if not order_len:
            return None
        return order[self.turn % order_len]
