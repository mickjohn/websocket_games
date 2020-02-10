from websocketgames.games.red_or_black import RedOrBlack
from websocketgames.games.base_card_guessing_game.states import GameStates
from websocketgames.games.players import Player
import pytest
from pytest import fixture
import jsonpickle

from tests.games.game_test_utils import MockWebsocket, mock_utils_send


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
    assert len(handler.p_reg.id_map) == 4
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
async def test_check_player_and_notify(mock_utils_send, four_player_game_lobby):
    (handler, websockets, __players) = four_player_game_lobby
    (ws1, *__) = websockets
    handler.state = GameStates.PLAYING
    assert await handler.check_player_and_notify(ws1)


@pytest.mark.asyncio
async def test_check_player_and_notify_sends_message_when_no_player(mock_utils_send, four_player_game_lobby):
    (handler, __, __) = four_player_game_lobby
    handler.state = GameStates.PLAYING
    non_existing_ws = MockWebsocket()
    assert await handler.check_player_and_notify(non_existing_ws) is False
