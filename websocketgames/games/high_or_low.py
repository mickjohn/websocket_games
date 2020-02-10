import logging
from websocketgames.games.base_card_guessing_game.handler import BasicCardGuessingGame

logger = logging.getLogger('websocketgames')


class HighOrLow():
    def __init__(self, game_code, cleanup_handler=None, options={}):
        logger.debug("Initialising HighOrLow game")
        self.basic_game = BasicCardGuessingGame(
            game_code,
            self.validate_guess,
            faceup_start=True,
            cleanup_handler=cleanup_handler,
            options=options
        )
        self.handle_message = self.basic_game.handle_message
        self.handle_close = self.basic_game.handle_close

    def validate_guess(self, guess, card, faceup_card):
        if guess == 'High':
            return card > faceup_card
        else:
            return card < faceup_card
