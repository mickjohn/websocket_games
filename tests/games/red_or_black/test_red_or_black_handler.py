from websocketgames.games.red_or_black.handler import RedOrBlack, Message
from websocketgames import code_generator
import pytest
from pytest_asyncio.plugin import asyncio
import json

code_generator.GAME_MODULUS_TABLE = {
    'RedOrBlack': 0
}


class MockWebsocket():
    def __init__(self):
        self.message_stack = []

    async def send(self, s):
        self.message_stack.append(s)

    def close(self):
        pass


@pytest.mark.asyncio
async def test_red_or_black_handler_can_create_game():
    mws = MockWebsocket()
    handler = RedOrBlack()
    message = {
        'game_id': '',
        'type': 'CreateGame',
        'data': {}
    }
    await handler.handle_message(message, mws)
    assert len(handler.games) == 1
    game_code = list(handler.games.keys())[0]
    expected_message = {
        'type': 'GameCreated',
        'game_code': game_code
    }
    assert mws.message_stack[0] == json.dumps(expected_message)


@pytest.mark.asyncio
async def test_red_or_black_handler_error_if_game_does_not_exist():
    mws = MockWebsocket()
    handler = RedOrBlack()
    message = {
        'game_id': 'does not exist',
        'type': 'AddPlayer',
        'data': {}
    }
    await handler.handle_message(message, mws)
    expected_message = {
        'type': 'Error',
        'error': 'no RedOrBlack game with code does not exist exists'
    }
    assert mws.message_stack[0] == json.dumps(expected_message)


@pytest.mark.asyncio
async def test_red_or_black_handler_can_add_player_to_game():
    mws = MockWebsocket()
    handler = RedOrBlack()
    game_id = handler._create_game()
    game = handler.games[game_id]

    message = {
        'game_id': game_id,
        'type': 'AddPlayer',
        'data': {
            'username': 'mickjohn'
        }
    }
    await handler.handle_message(message, mws)
    mickjohn_user_id = game.usernames_map['mickjohn'].user_id
    expected_message = {
        'type': 'PlayerAdded',
        'id': mickjohn_user_id,
    }
    assert handler.players_id[mickjohn_user_id] == (mws, game_id)
    assert handler.players_websocket[mws] == (mickjohn_user_id, game_id)
    assert mws.message_stack[0] == json.dumps(expected_message)


@pytest.mark.asyncio
async def test_red_or_black_handler_error_when_user_already_added_to_game():
    mws = MockWebsocket()
    handler = RedOrBlack()
    game_id = handler._create_game()

    message = {
        'game_id': game_id,
        'type': 'AddPlayer',
        'data': {
            'username': 'mickjohn'
        }
    }
    # Add user once
    await handler.handle_message(message, mws)
    # Add user again
    await handler.handle_message(message, mws)
    expected_message = {
        'type': 'Error',
        'error': "User with name mickjohn already exists in game",
    }
    assert mws.message_stack[1] == json.dumps(expected_message)


@pytest.mark.asyncio
async def test_handle_close():
    mws = MockWebsocket()
    handler = RedOrBlack()
    game_id = handler._create_game()

    message = {
        'game_id': game_id,
        'type': 'AddPlayer',
        'data': {
            'username': 'mickjohn'
        }
    }
    # Add user once
    await handler.handle_message(message, mws)
    # Add user again
    await handler.handle_message(message, mws)
    expected_message = {
        'type': 'Error',
        'error': "User with name mickjohn already exists in game",
    }
    assert mws.message_stack[1] == json.dumps(expected_message)
