import logging
import asyncio

from websocketgames.games.turn_based import TurnBasedGame
from websocketgames.deck import Deck
from websocketgames.games.base_card_guessing_game import validator
from websocketgames.games import utils
from websocketgames.games.base_card_guessing_game.states import GameStates
from websocketgames.games.base_card_guessing_game.stats import Outcome, Stats

logger = logging.getLogger('websocketgames')


class BaseCardGuessingGame(TurnBasedGame):

    def __init__(self, game_code, validate_guess=None, faceup_start=False, cleanup_handler=None, options={}):
        super().__init__(game_code, cleanup_handler, timeout_seconds=30)
        self.turn = 0
        self.turn_sleep_s = 1
        self.end_sleep_s = 1
        self.state = GameStates.LOBBY
        self.deck = Deck(shuffled=True)
        self.deck.cards = self.deck.cards[0:options.get('number_of_cards', 52)]

        if faceup_start:
            self.faceup_card = self.deck.draw_card()
        else:
            self.faceup_card = None
        self.penalty_increment = options.get('penalty_increment', 1)
        self.penalty_start = options.get('penalty_start', 1)
        self.penalty = options.get('penalty_start', 1)
        self.shutting_down = False
        self.stats = Stats()

        # Asyncio task for the cleanup callback
        self.cleanup_task = None

    def __repr__(self):
        return (
            f"\n[{self.game_code}]: registered_players: {self.p_reg}\n"
            f"[{self.game_code}]: turn: {self.turn}\n"
            f"[{self.game_code}]: state: {self.state}\n"
            f"[{self.game_code}]: owner: {self.owner}\n"
            f"[{self.game_code}]: order: {self.p_reg.get_order()}\n"
            f"[{self.game_code}]: cards left: {len(self.deck.cards)}\n"
            f"[{self.game_code}]: faceup card: {self.faceup_card}\n"
            f"[{self.game_code}]: player registery: {self.p_reg}\n"
            f"[{self.game_code}]: client registery: {self.c_reg}\n"
            f"[{self.game_code}]: history: {self.get_full_game_state()}\n"
        )

    def _debug(self):
        logger.debug(self)

    def validate_guess(self, guess, card, faceup_card):
        raise NotImplementedError

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
            player = await self.activate_player(websocket, message)
            await utils.send_message(
                websocket,
                'YouJoined',
                player=player,
                game_state=self.get_full_game_state(),
            )
        elif msg_type == 'StartGame':
            await self.start_game(websocket, message)
        elif msg_type == 'PlayTurn':
            await self.play_turn(websocket, message)

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

    async def can_play_turn(self, websocket, player):
        order = self.p_reg.get_order()
        current_player = self.p_reg.get_order()[self.turn % len(order)]
        if self.state != GameStates.PLAYING:
            logger.error(f"Game is not in playing state")
            await utils.send_message(websocket, 'GameNotStarted')
            return False

        if player != current_player:
            logger.error(f"It's not the turn of '{player.username}'")
            await utils.send_message(websocket, 'NotPlayerTurn')
            return False

        if not len(self.deck.cards):
            logger.error('No cards left!')
            return False
        return True

    async def play_turn(self, websocket, msg):
        '''
        Take a players guess and progress the game by one turn, and send the
        outcome to all the players in the game.
        '''
        # Before processing the turn, sleep for some time to add to the suspense
        await asyncio.sleep(self.turn_sleep_s)
        logger.debug('Playing turn')

        # Check if the websocket exists and has a player
        if not await self.check_player_and_notify(websocket):
            return

        player = self.c_reg.clients[websocket].player

        # Check if the player can play this turn
        if not await self.can_play_turn(websocket, player):
            return

        # The penalty returned to the player
        return_penalty = self.penalty
        guess = msg['guess']
        card = self.deck.draw_card()
        correct = self.validate_guess(guess, card, self.faceup_card)
        logger.info(
            f"guess for {player.username}: card={card} guess={guess} correct={correct}")

        outcome = Outcome(player, self.turn, guess,
                          correct, return_penalty, card, self.faceup_card)
        self.stats.update(outcome)
        self.faceup_card = card

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
            outcome=outcome,
        )

        self.turn += 1

        if len(self.deck.cards) == 0:
            logger.info(
                f"{self.game_code}: Deck empty, finishing game. Sleeping for {self.end_sleep_s} first")
            await asyncio.sleep(self.end_sleep_s)
            self.state = GameStates.FINISHED
            await utils.broadcast_message(
                self.c_reg.websockets(),
                'GameFinished',
                stats=self.stats.get_stats(),
            )

    def get_full_game_state(self):
        '''
        Gather info about the game and place it into a dict. This will be sent to
        a player when they join the game.
        '''
        state = {
            'players': list(self.p_reg.id_map.values()),
            'turn': self.turn,
            'state': str(self.state),
            'owner': self.owner,
            'order': self.p_reg.get_order(),
            'stats': self.stats.get_stats(),
            'history': self.stats.outcomes,
            'penalty': self.penalty,
            'cards_left': len(self.deck.cards),
            'faceup_card': self.faceup_card,
        }
        return state

    def get_current_player(self):
        '''
        Get the player who's turn it is
        '''
        if self.state != GameStates.PLAYING:
            return None

        order = self.p_reg.get_order()
        order_len = len(order)
        if not order_len:
            return None
        return order[self.turn % order_len]
