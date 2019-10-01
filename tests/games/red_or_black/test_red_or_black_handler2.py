from websocketgames.games.red_or_black.handler2 import RedOrBlack, Client, GameStates
from websocketgames.games.red_or_black.players import Player
from websocketgames.games.red_or_black import utils
from websocketgames import code_generator
import pytest
from pytest_asyncio.plugin import asyncio
from pytest import fixture
import jsonpickle


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

# @fixture
# def four_player_game_lobby():


@fixture
def mock_utils_send(monkeypatch):
    class MockUtils():
        def __init__(self):
            self.msgs = []
            self.broadcast = []

        async def send_message(self, ws, msg_type, **kwargs):
            msg = jsonpickle.encode(
                {'type': msg_type, **kwargs},
                unpicklable=False
            )
            self.msgs.append(jsonpickle.decode(msg))

        async def broadcast_message(self, ws, msg_type, skip=[], **kwargs):
            json_msg = jsonpickle.encode(
                {'type': msg_type, **kwargs},
                unpicklable=False
            )
            msg = jsonpickle.decode(json_msg)
            utils.remove_sensitive_info_from_message(msg)
            self.broadcast.append(msg)

        def __repr__(self):
            return (
                f"msgs = {self.msgs}\n"
                f"broadcast = {self.broadcast}\n"
            )

    mock_utils = MockUtils()
    monkeypatch.setattr(
        'websocketgames.games.red_or_black.utils.send_message',
        mock_utils.send_message,
    )
    monkeypatch.setattr(
        'websocketgames.games.red_or_black.utils.broadcast_message',
        mock_utils.broadcast_message,
    )
    return mock_utils


@pytest.mark.asyncio
async def test_register_player_works():
    ws = MockWebsocket()
    msg = {'type': 'Register', 'username': 'abc'}
    handler = RedOrBlack('BAAA')
    player = await handler.register_player(msg, ws)
    exmsg = jsonpickle.encode({
        'type': 'Registered',
        'user_id': player.user_id
    }, unpicklable=False)
    assert ws.message_stack[0] == exmsg


@pytest.mark.asyncio
async def test_register_player_errors_when_user_already_exists():
    ws = MockWebsocket()
    msg = {'type': 'Register', 'username': 'abc'}
    handler = RedOrBlack('BAAA')
    await handler.register_player(msg, ws)
    await handler.register_player(msg, ws)
    exmsg = jsonpickle.encode({
        'type': 'Error',
        'error': 'User with name abc already registered in game',
        'error_type': 'UserAlreadyRegistered',
    }, unpicklable=False)
    assert ws.message_stack[1] == exmsg


@pytest.mark.asyncio
async def test_activate_player():
    ws = MockWebsocket()
    handler = RedOrBlack('BAAA')
    player = await handler.register_player({'type': 'Register', 'username': 'abc'}, ws)
    assert not player.active
    await handler.activate_player({'type': 'Activate', 'user_id': player.user_id}, ws)
    assert player.active
    assert ws.message_stack[1] == jsonpickle.encode(
        {
            'type': 'YouJoined',
            'player': player,
            'game_state': handler.get_full_game_state()
        },
        unpicklable=False
    )


@pytest.mark.asyncio
async def test_handle_close(mock_utils_send):
    # Setup
    ws1 = MockWebsocket()
    ws2 = MockWebsocket()
    handler = RedOrBlack('ABCD')
    handler.state = GameStates.PLAYING
    p1 = Player('mick', '123', active=True)
    p2 = Player('john', '456', active=True)
    handler.owner = p1
    handler.p_reg.add_player(p1)
    handler.p_reg.add_player(p2)
    handler.c_reg.connect(ws1, p1)
    handler.c_reg.connect(ws2, p2)

    # Test
    assert len(handler.p_reg.get_order()) == 2
    await handler.handle_close(ws1)
    assert len(handler.p_reg.id_map) == 2
    assert len(handler.p_reg.get_order()) == 1
    assert len(handler.c_reg.clients) == 1
    assert handler.owner == p2
    assert mock_utils_send.broadcast == [
        {'type': 'PlayerDisconnected', 'player': {
            'username': 'mick', 'active': False}},
        {'type': 'NewOwner', 'owner': {
            'username': 'john', 'active': True}},
        {'type': 'Order', 'order': [
            {'username': 'john', 'active': True}]}
    ]


@pytest.mark.asyncio
async def test_get_current_player():
    handler = RedOrBlack('ABCD')
    handler.state = GameStates.PLAYING
    p1 = Player('mick', '123', active=True)
    p2 = Player('john', '456', active=True)
    handler.p_reg.add_player(p1)
    handler.p_reg.add_player(p2)
    assert handler.get_current_player() == p1
    handler.turn += 1
    assert handler.get_current_player() == p2
    handler.turn += 1
    assert handler.get_current_player() == p1
    p1.active = False
    assert handler.get_current_player() == p2
