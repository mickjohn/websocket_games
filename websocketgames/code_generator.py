import random
from websocketgames import games


class GameNotFound(Exception):
    pass


_MAX_CODE = 456975  # i.e 456975 == zzzz
_MIN_CODE = 17576  # i.e baaa (smallets 4 'digit' code)
_MODULUS = 97  # Games will be identified by their modulus. Modulus of 97 allows 97 differnt game types
_BASE = 26  # Base 26 i.e A-Z
_DIGITS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

_LOWER_BOUND = _MIN_CODE + _MODULUS
_HIGHER_BOUND = _MAX_CODE - _MODULUS + 1

# When divided by the MODULUS, the remainder will identify the game
# This cannot be dynamically created. The client will need to know this modulus
# table
GAME_MODULUS_TABLE = {
    'RedOrBlack': 0
}


def generate_code(game):
    return _convert_to_code(_generate_number(game))


def _generate_number(game):
    if game not in GAME_MODULUS_TABLE:
        raise GameNotFound(f"{game} not found in mod table")
    mod = GAME_MODULUS_TABLE[game]
    code = random.randint(_LOWER_BOUND, _HIGHER_BOUND)
    code = code - (code % _MODULUS)
    code += mod
    return code


def _convert_to_code(code):
    temp_code = code
    converted_code = []
    index = 1
    while(True):
        index += 1
        mod = temp_code % _BASE
        converted_code.append(_DIGITS[mod])
        temp_code = temp_code // _BASE
        if temp_code == 0:
            break
    converted_code.reverse()
    return ''.join(converted_code)
