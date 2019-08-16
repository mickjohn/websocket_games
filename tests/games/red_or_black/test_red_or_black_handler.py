from websocketgames.games.red_or_black import handler
from websocketgames.games.red_or_black.handler import RedOrBlack, Client
from websocketgames import code_generator
import pytest
from pytest_asyncio.plugin import asyncio
from pytest import fixture
# import json
import jsonpickle

code_generator.GAME_MODULUS_TABLE = {
    'RedOrBlack': 0
}


@fixture
def set_sensitive_array():
    handler.SENSITIVE = [
        'user_id'
    ]


class MockWebsocket():
    def __init__(self):
        self.message_stack = []
        self.broadcast_stack = []
        self.open = True

    async def send(self, s):
        # decode message to check if it's a broadcast message or not
        msg_dict = jsonpickle.decode(s)
        if 'broadcast' in msg_dict and msg_dict['broadcast']:
            self.broadcast_stack.append(s)
        else:
            self.message_stack.append(s)

    def close(self):
        self.open = False


def test_remove_sensitive_info_from_message(set_sensitive_array):
    msg = {
        'type': 'TestMessage',
        'user_id': '111-222-333',
        'nested': {
            'x': 123,
            'user_id': '4444-5555'
        }
    }

    # msg = {
    #     'type': 'PlayerAdded',
    #     'broadcast': True,
    #     'player': {
    #         'username': 'mickjohn',
    #         'active': True
    #     }
    # }

    expected_msg = {
        'type': 'TestMessage',
        'nested': {
            'x': 123
        }
    }

    handler._remove_sensitive_info_from_message(msg)
    msg == expected_msg


@pytest.mark.asyncio
async def test_red_or_black_handler_can_create_game():
    mws = MockWebsocket()
    handler = RedOrBlack()
    message = {
        'type': 'CreateGame'
    }
    await handler.handle_message(message, mws)
    assert len(handler.games) == 1
    game_code = list(handler.games.keys())[0]
    expected_message = {
        'type': 'GameCreated',
        'game_code': game_code
    }
    assert mws.message_stack[0] == jsonpickle.encode(
        expected_message, unpicklable=False)


@pytest.mark.asyncio
async def test_red_or_black_handler_error_if_game_does_not_exist():
    mws = MockWebsocket()
    handler = RedOrBlack()
    message = {
        'game_id': 'does not exist',
        'type': 'AddPlayer',
        'username': 'mickjohn'
    }
    await handler.handle_message(message, mws)
    expected_message = {
        'type': 'Error',
        'error': 'no RedOrBlack game with code does not exist exists'
    }
    assert mws.message_stack[0] == jsonpickle.encode(
        expected_message, unpicklable=False)


@pytest.mark.asyncio
async def test_red_or_black_handler_can_add_player_to_game():
    mws = MockWebsocket()
    handler = RedOrBlack()
    game_id = handler._create_game()
    game = handler.games[game_id]

    message = {
        'game_id': game_id,
        'type': 'AddPlayer',
        'username': 'mickjohn'
    }
    await handler.handle_message(message, mws)
    mickjohn_user_id = game.usernames_map['mickjohn'].user_id

    expected_client = Client(mickjohn_user_id, game_id, mws)
    assert handler.clients[mickjohn_user_id] == expected_client
    assert handler.websockets[mws] == expected_client

    expected_message = {
        'type': 'PlayerAdded',
        'player': game.usernames_map['mickjohn']
    }

    print(f"stack = {mws.message_stack}")
    assert mws.message_stack[0] == jsonpickle.encode(
        expected_message, unpicklable=False)


@pytest.mark.asyncio
async def test_red_or_black_handler_error_when_user_already_added_to_game():
    mws = MockWebsocket()
    handler = RedOrBlack()
    game_id = handler._create_game()

    message = {
        'game_id': game_id,
        'type': 'AddPlayer',
        'username': 'mickjohn'
    }
    # Add user once
    await handler.handle_message(message, mws)
    # Add user again
    await handler.handle_message(message, mws)
    expected_message = {
        'type': 'Error',
        'error': "User with name mickjohn already exists in game",
    }
    assert mws.message_stack[1] == jsonpickle.encode(
        expected_message, unpicklable=True)


@pytest.mark.asyncio
async def test_handle_close():
    mws = MockWebsocket()
    handler = RedOrBlack()
    game_id = handler._create_game()

    message = {
        'game_id': game_id,
        'type': 'AddPlayer',
        'username': 'mickjohn'
    }
    # Add user once
    await handler.handle_message(message, mws)
    # Add user again
    await handler.handle_message(message, mws)
    expected_message = {
        'type': 'Error',
        'error': 'User with name mickjohn already exists in game',
    }

    assert mws.message_stack[1] == jsonpickle.encode(
        expected_message, unpicklable=False)

    expected_broadcast_message = {
        "broadcast": True,
        "type": "PlayerAdded",
        "player": {
            "active": True,
            "username": "mickjohn"
        },
    }

    # Broadcast should skip origin websocket
    assert len(mws.broadcast_stack) == 0
