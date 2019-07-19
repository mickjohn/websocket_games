from websocketgames.games.red_or_black import handler
from websocketgames.games.red_or_black.handler import Message
import pytest


def test_init_message():
    msg = {"game_id": "123saa", "type": "CreateGame", "data": {}}
    message = Message(msg)

    assert message.game_id == '123saa'
    assert message.data == {}
    assert message.type == 'CreateGame'


def test_init_message_fails_when_no_game_id():
    msg = {
        'data': {}
    }
    with pytest.raises(Exception) as e:
        Message(msg)
    assert "Field 'game_id' is missing" in str(e.value)


def test_init_message_fails_with_no_data():
    msg = {
        'game_id': 'dsfndsf',
        'notdata': {}
    }
    with pytest.raises(Exception) as e:
        Message(msg)
    assert "Field 'data' is missing" in str(e.value)

def test_init_message_fails_with_no_type():
    msg = {
        'game_id': 'dsfndsf',
        'notype': '',
        'data': {}
    }
    with pytest.raises(Exception) as e:
        Message(msg)
    assert "Field 'type' is missing" in str(e.value)


def test_init_message_fails_with_unknown_message_type():
    handler.ALLOWED_MESSAGES = [
        'AllowedMessage'
    ]
    msg = {
        'game_id': 'dsfndsf',
        'type': 'jfndsf',
        'data': {}
    }
    with pytest.raises(Exception) as e:
        Message(msg)
    assert "Unknown message type 'jfndsf" in str(e.value)
