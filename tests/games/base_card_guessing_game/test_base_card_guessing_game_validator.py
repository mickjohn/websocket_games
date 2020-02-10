from websocketgames.games.base_card_guessing_game import validator
import pytest
from pytest import fixture
from jsonschema.exceptions import ValidationError


@fixture
def set_allowed_messages():
    validator.ALLOWED_MESSAGES = [
        'CreateGame',
        'AddPlayer',
    ]


@fixture
def set_schemas():
    validator.schemas = {
        'CreateGame': {
            "type": "object",
            "required": ["type"],
            "additionalProperties": False,
            "properties": {
                "type": {"type": "string"},
            }
        },

        'AddPlayer': {
            "type": "object",
            "required": ["type", "game_id", "username"],
            "additionalProperties": False,
            "properties": {
                "type": {"type": "string"},
                "game_id": {"type": "string"},
                "username": {"type": "string"},
            }
        },
    }


def test_validator_works_with_valid_message(set_allowed_messages, set_schemas):
    validator.validate_msg({'type': 'CreateGame'})
    validator.validate_msg(
        {'type': 'AddPlayer', 'game_id': 'QWER', 'username': 'mick'})


def test_validator_fails_when_type_is_missing(set_allowed_messages):
    with pytest.raises(Exception) as e:
        validator.validate_msg({'qwerty': 'FailPlease'})
    assert "Field 'type' is missing" == str(e.value)


def test_validator_fails_when_type_is_unkown(set_allowed_messages):
    with pytest.raises(Exception) as e:
        validator.validate_msg({'type': 'FailPlease'})
    assert "Unknown message type 'FailPlease'" == str(e.value)


def test_validator_fails_when_msg_is_incorrect(set_allowed_messages, set_schemas):
    with pytest.raises(ValidationError) as e:
        validator.validate_msg({'type': 'CreateGame', 'extra': 'data'})
