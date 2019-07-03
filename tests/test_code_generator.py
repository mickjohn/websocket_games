from websocketgames import code_generator
from websocketgames.code_generator import GameNotFound
import pytest


class RedOrBlack():
    pass


class DefinitelyNotRegistered():
    def __init__(self):
        self.codes = set()
        name = type(self).__name__
        if name not in code_generator.GAME_MODULUS_TABLE:
            raise Exception(f"{name} not registered in GAME_MODULUS_TABLE")


def prepare_code_generator():
    '''
    Ensure that the code generator has the expected values
    '''
    maxcode = 456975
    mincode = 17576
    modulus = 97
    code_generator._MAX_CODE = maxcode
    code_generator._MIN_CODE = mincode
    code_generator._MODULUS = modulus
    code_generator._BASE = 26
    code_generator._DIGITS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    code_generator._LOWER_BOUND = mincode + modulus
    code_generator._HIGHER_BOUND = maxcode - modulus + 1
    code_generator.GAME_MODULUS_TABLE = {}


def test_exception_raised_if_game_not_registered():
    with pytest.raises(Exception) as e:
        __d = DefinitelyNotRegistered()
    assert "DefinitelyNotRegistered not registered in GAME_MODULUS_TABLE" in str(
        e.value)


def test_exception_raised_if_game_not_found_in_table():
    with pytest.raises(GameNotFound) as e:
        code_generator.generate_code('not a game')
    assert "not a game not found in mod table" in str(e.value)


def test_code_is_generated_with_modulus():
    prepare_code_generator()
    code_generator.GAME_MODULUS_TABLE['test'] = 27
    generated_num = code_generator._generate_number('test')
    assert generated_num % code_generator._MODULUS == 27


def test_code_is_converted_to_different_base():
    prepare_code_generator()
    assert code_generator._convert_to_code(25) == 'Z'
    assert code_generator._convert_to_code(456975) == 'ZZZZ'
    assert code_generator._convert_to_code(26) == 'BA'
