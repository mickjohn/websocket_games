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


@fixture
def four_player_game_lobby():
    '''
    Create a game with the following properties:
        - The Player registery has 4 players
        - The 4th player is inactive
        - The Client registery has 3 Clients
        - Game is in LOBBY state
        - The owner is p1
    '''
    handler = RedOrBlack('ABCD')
    ws1 = MockWebsocket()
    ws2 = MockWebsocket()
    ws3 = MockWebsocket()
    wesockets = [ws1, ws2, ws3]
    p1 = Player('mick', '123', active=True)
    p2 = Player('john', '456', active=True)
    p3 = Player('dracula', '789', active=True)
    p4 = Player('dough boy', '369', active=False)
    players = [p1, p2, p3, p4]
    handler.owner = p1
    handler.p_reg.add_player(p1)
    handler.p_reg.add_player(p2)
    handler.p_reg.add_player(p3)
    handler.p_reg.add_player(p4)
    handler.c_reg.connect(ws1, p1)
    handler.c_reg.connect(ws2, p2)
    handler.c_reg.connect(ws3, p3)
    return (handler, wesockets, players)


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
    player = await handler.register_player(ws, msg)
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
    await handler.register_player(ws, msg)
    await handler.register_player(ws, msg)
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
    player = await handler.register_player(ws, {'type': 'Register', 'username': 'abc'})
    assert not player.active
    await handler.activate_player(ws, {'type': 'Activate', 'user_id': player.user_id})
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
async def test_handle_close(mock_utils_send, four_player_game_lobby):
    # Setup
    (handler, websockets, players) = four_player_game_lobby
    (ws1, *_) = websockets
    (p1, p2, *_) = players
    handler.state = GameStates.PLAYING
    handler.owner = p1

    assert len(handler.p_reg.get_order()) == 3
    await handler.handle_close(ws1)
    assert len(handler.p_reg.id_map) == 3
    assert len(handler.p_reg.get_order()) == 2
    assert len(handler.c_reg.clients) == 2
    assert handler.owner == p2
    assert mock_utils_send.broadcast == [
        {'type': 'PlayerDisconnected', 'player': {
            'username': 'mick', 'active': False}},
        {'type': 'NewOwner', 'owner': {
            'username': 'john', 'active': True}},
        {'type': 'OrderChanged', 'order': [
            {'username': 'john', 'active': True},
            {'username': 'dracula', 'active': True}
        ]}
    ]


@pytest.mark.asyncio
async def test_start_game(mock_utils_send, four_player_game_lobby):
    (handler, websockets, __players) = four_player_game_lobby
    (ws1, __ws2, *_) = websockets
    assert handler.state == GameStates.LOBBY
    await handler.start_game(ws1, {'type': 'StartGame', 'user_id': '123'})
    assert handler.state == GameStates.PLAYING
    assert mock_utils_send.broadcast == [
        {'type': 'GameStarted'}
    ]


@pytest.mark.asyncio
async def test_start_game_fails_is_user_is_not_owner(mock_utils_send, four_player_game_lobby):
    (handler, websockets, __players) = four_player_game_lobby
    (__ws1, ws2, __ws3) = websockets
    await handler.start_game(ws2, {'type': 'StartGame', 'user_id': '456'})
    assert handler.state == GameStates.LOBBY
    assert mock_utils_send.broadcast == []
    assert mock_utils_send.msgs == [
        {
            'type': 'Error',
            'error': 'User with id 456 not allowed to start the game'
        }
    ]


@pytest.mark.asyncio
async def test_get_current_player(four_player_game_lobby):
    (handler, __websockets, players) = four_player_game_lobby
    (p1, p2, p3, p4) = players
    handler.state = GameStates.PLAYING
    assert handler.get_current_player() == p1
    handler.turn += 1
    assert handler.get_current_player() == p2
    handler.turn += 1
    assert handler.get_current_player() == p3
    # p4 should be skipped because it's inactive
    handler.turn += 1
    assert handler.get_current_player() == p1
