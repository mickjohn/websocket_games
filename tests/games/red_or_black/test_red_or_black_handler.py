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

    expected_msg = {
        'type': 'TestMessage',
        'nested': {
            'x': 123
        }
    }

    handler._remove_sensitive_info_from_message(msg)
    msg == expected_msg


@pytest.mark.asyncio
async def test_can_create_game():
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
async def test_error_if_game_does_not_exist():
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
async def test_can_add_player_to_game():
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
async def test_error_when_user_already_added_to_game():
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


@pytest.mark.asyncio
async def test_register_player():
    mws = MockWebsocket()
    handler = RedOrBlack()
    game_id = handler._create_game()

    message = {
        "type": "Register",
        "username": "mickjohn",
        "game_id": game_id,
    }

    await handler.handle_message(message, mws)
    game = handler.games[game_id]
    uid = list(game.registered_ids.keys())[0]
    expected_msg = jsonpickle.encode({
        "type": "Registered",
        "user_id": uid,
    }, unpicklable=True)
    assert len(mws.message_stack) == 1
    assert mws.message_stack[0] == expected_msg


@pytest.mark.asyncio
async def test_register_player_sends_error_if_player_already_registered():
    mws = MockWebsocket()
    handler = RedOrBlack()
    game_id = handler._create_game()

    message = {
        "type": "Register",
        "username": "mickjohn",
        "game_id": game_id,
    }

    await handler.handle_message(message, mws)

    # Send message again
    await handler.handle_message(message, mws)
    handler.games[game_id]
    expected_msg = jsonpickle.encode({
        "error": "User with name mickjohn already registered in game",
        "type": "Error"
    }, unpicklable=True)
    assert len(mws.message_stack) == 2
    assert mws.message_stack[1] == expected_msg


@pytest.mark.asyncio
async def test_activate_player():
    mws = MockWebsocket()
    handler = RedOrBlack()
    game_id = handler._create_game()
    game = handler.games[game_id]
    uid = game.register_player('mickjohn').user_id

    # Check that the inactive ID is removed
    handler.inactive_player_ids.add(uid)
    msg = {
        'type': 'Activate', 'game_id': game_id, 'user_id': uid,
    }

    await handler.handle_message(msg, mws)
    assert len(game.usernames_map) == 1
    assert len(game.id_map) == 1
    assert handler.clients[uid] == Client(uid, game_id, mws)
    assert handler.websockets[mws] == Client(uid, game_id, mws)
    assert len(handler.inactive_player_ids) == 0

    expected_msg = jsonpickle.encode({
        'type': 'YouJoined',
        'player': game.id_map[uid],
        'game_state': game.get_full_game_state(),
    }, unpicklable=False)

    assert len(mws.message_stack) == 1
    assert mws.message_stack[0] == expected_msg
    # The websocket should be skipped by the broadcast message
    assert len(mws.broadcast_stack) == 0


@pytest.mark.asyncio
async def test_activate_player_fails_if_player_not_registered():
    mws = MockWebsocket()
    handler = RedOrBlack()
    game_id = handler._create_game()

    uid = 'sdjnbfsdbnlsnf'
    msg = {
        'type': 'Activate', 'game_id': game_id, 'user_id': uid,
    }

    await handler.handle_message(msg, mws)

    expected_msg = jsonpickle.encode({
        'type': 'Error',
        'error': f"User with id sdjnbfsdbnlsnf does not exist in game {game_id}",
    }, unpicklable=False)

    assert len(mws.message_stack) == 1
    assert mws.message_stack[0] == expected_msg


@pytest.mark.asyncio
async def test_activate_player_idempotent():
    mws = MockWebsocket()
    handler = RedOrBlack()
    game_id = handler._create_game()
    game = handler.games[game_id]
    uid = game.register_player('mickjohn').user_id

    # Check that the inactive ID is removed
    handler.inactive_player_ids.add(uid)
    msg = {
        'type': 'Activate', 'game_id': game_id, 'user_id': uid,
    }

    await handler.handle_message(msg, mws)
    state_before = (
        game.usernames_map,
        game.id_map,
        handler.clients,
        handler.websockets,
        handler.inactive_player_ids,
    )
    assert len(mws.message_stack) == 1

    # Activate user again
    await handler.handle_message(msg, mws)
    state_after = (
        game.usernames_map,
        game.id_map,
        handler.clients,
        handler.websockets,
        handler.inactive_player_ids,
    )

    assert state_before == state_after
    assert len(mws.message_stack) == 2


@pytest.mark.asyncio
async def test_start_game():
    mws = MockWebsocket()
    handler = RedOrBlack()
    game_id = handler._create_game()
    game = handler.games[game_id]
    uid = game.register_player('mickjohn').user_id

    await handler.handle_message({
        'type': 'Activate', 'game_id': game_id, 'user_id': uid,
    }, mws)

    assert game.is_lobby()

    msg = {
        'type': 'StartGame', 'user_id': uid, 'game_id': game_id,
    }

    await handler.handle_message(msg, mws)
    assert game.is_playing()
    assert len(mws.broadcast_stack) == 1

    expected_msg = jsonpickle.encode({
        'broadcast': True,
        'type': 'GameStarted'
    }, unpicklable=False)

    assert mws.broadcast_stack[0] == expected_msg


@pytest.mark.asyncio
async def test_start_game_fails_if_player_is_not_owner():
    mws = MockWebsocket()
    handler = RedOrBlack()
    game_id = handler._create_game()
    game = handler.games[game_id]
    game.add_player_by_username('mickjohn')
    uid = game.add_player_by_username('mickjohn2')

    assert game.is_lobby()

    msg = {
        'type': 'StartGame', 'user_id': uid, 'game_id': game_id,
    }

    await handler.handle_message(msg, mws)
    assert len(mws.message_stack) == 1

    expected_msg = jsonpickle.encode({
        'type': 'Error',
        'error': f'User with id {uid} not allowed to start the game'
    }, unpicklable=False)

    assert mws.message_stack[0] == expected_msg
