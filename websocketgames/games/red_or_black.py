import logging
from websocketgames.games.base_card_guessing_game.handler import BaseCardGuessingGame

logger = logging.getLogger('websocketgames')


class RedOrBlack(BaseCardGuessingGame):
    def __init__(self, game_code, cleanup_handler=None, options={}):
        logger.debug("Initialising RedOrBlack game")
        super().__init__(
            game_code,
            faceup_start=False,
            cleanup_handler=cleanup_handler,
            options=options
        )

    def validate_guess(self, guess, card, faceup_card):
        return guess == card.get_colour()
