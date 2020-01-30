import logging
import asyncio


from websocketgames.deck import Deck
from websocketgames.games.high_or_low import validator
from websocketgames.games.high_or_low import utils
from websocketgames.games.turn_based import TurnBasedGame
from websocketgames.games.high_or_low.states import GameStates
from websocketgames.games.high_or_low.stats import Outcome, Stats

logger = logging.getLogger('websocketgames')


class HighOrLow(TurnBasedGame):

    def __init__(self, game_code, cleanup_handler=None, options={}):
        super().__init__(game_code, cleanup_handler, timeout_seconds=30)
        self.turn = 0
        self.turn_sleep_s = 1
        self.end_sleep_s = 1
        self.state = GameStates.LOBBY
        self.owner = None
        self.deck = Deck(shuffled=True)
        self.deck.cards = self.deck.cards[0:options.get('number_of_cards', 52)]
        self.current_card = self.deck.draw_card()
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
            f"[{self.game_code}]: player registery: {self.p_reg}\n"
            f"[{self.game_code}]: client registery: {self.c_reg}\n"
            f"[{self.game_code}]: history: {self.get_full_game_state()}\n"
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

    async def play_turn(self, websocket, msg):
        '''
        Take a players guess and progress the game by one turn, and send the
        outcome to all the players in the game.
        '''
        # Before processing the turn, sleep for some time to add to the suspense
        await asyncio.sleep(self.turn_sleep_s)
        logger.debug('Playing turn')
        if websocket not in self.c_reg.clients:
            await utils.send_user_not_found(websocket)
            return

        if self.c_reg.clients[websocket].player is None:
            await utils.send_user_not_found(websocket)
            return

        guess = msg['guess']
        if guess not in ['High', 'Low']:
            await utils.send_message(
                websocket,
                'Error',
                error=f"Guess must be 'High' or 'Low', got '{guess}'"
            )
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

        card = self.deck.draw_card()
        if guess == 'High':
            correct = card > self.current_card
        else:
            correct = card < self.current_card
        self.current_card = card

        logger.debug(
            f"guess for {player.username}: card={card} guess={guess} correct={correct}")

        outcome = Outcome(player, self.turn, guess,
                          correct, card, return_penalty)
        self.stats.update(outcome)

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
            current_card=self.current_card,
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
            'current_card': self.current_card,
            'penalty': self.penalty,
            'cards_left': len(self.deck.cards),
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
