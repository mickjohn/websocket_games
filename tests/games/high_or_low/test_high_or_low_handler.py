from websocketgames.games.high_or_low.handler import HighOrLow, GameStates
from websocketgames.games.players import Player
from websocketgames.games.clients import Client
from websocketgames.games.high_or_low import utils
from websocketgames import code_generator, deck
from tests.games.game_test_utils import MockWebsocket

import pytest
from pytest_asyncio.plugin import asyncio
from pytest import fixture
import jsonpickle


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
    handler = HighOrLow('ABCD')
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
def outcomes():
    '''
    Return outcome of 10 turns with three players
    Every card is Ace of Hearts
    player 1: all RED and all CORRECT
    player 2: one RED and ONE CORRECT
    player 3: zero RED and zero CORRECT
    '''
    return [
        {'player': Player('mick', '123'), 'turn': 0, 'guess': 'Red',
         'correct': True, 'card': 'A of Hearts', 'penalty': 1},
        {'player': Player('john', '456'), 'turn': 1,
         'guess': 'Red', 'correct': True, 'card': 'A of Hearts', 'penalty': 2},
        {'player': Player('dracula', '789'), 'turn': 2,
         'guess': 'Black', 'correct': False, 'card': 'A of Hearts', 'penalty': 3},
        {'player': Player('mick', '123'), 'turn': 3,
         'guess': 'Red', 'correct': True, 'card': 'A of Hearts', 'penalty': 1},
        {'player': Player('john', '456'), 'turn': 4,
         'guess': 'Black', 'correct': False, 'card': 'A of Hearts', 'penalty': 2},
        {'player': Player('dracula', '789'), 'turn': 5,
         'guess': 'Black', 'correct': False, 'card': 'A of Hearts', 'penalty': 1},
        {'player': Player('mick', '123'), 'turn': 6,
         'guess': 'Red', 'correct': True, 'card': 'A of Hearts', 'penalty': 1},
        {'player': Player('john', '456'), 'turn': 7,
         'guess': 'Black', 'correct': False, 'card': 'A of Hearts', 'penalty': 2},
        {'player': Player('dracula', '789'), 'turn': 8,
         'guess': 'Black', 'correct': False, 'card': 'A of Hearts', 'penalty': 1}
    ]


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
        'websocketgames.games.high_or_low.utils.send_message',
        mock_utils.send_message,
    )
    monkeypatch.setattr(
        'websocketgames.games.high_or_low.utils.broadcast_message',
        mock_utils.broadcast_message,
    )
    return mock_utils


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
async def test_play_turn(mock_utils_send, four_player_game_lobby):
    (handler, websockets, players) = four_player_game_lobby
    (ws1, *_) = websockets
    (p1, *_) = players
    # Set cards to something we know
    handler.state = GameStates.PLAYING
    handler.turn_sleep_s = 0
    handler.deck.cards = [deck.Card('Ace', 'Clubs')] * 10
    handler.current_card = deck.Card('King', 'Hearts')

    # Guess correct answer
    msg = {'type': 'PlayTurn', 'guess': 'Low'}
    await handler.play_turn(ws1, msg)
    expected_message = {
        'type': 'GuessOutcome',
        'guess': 'Low',
        'cards_left': 9,
        'turn': 0,
        'correct': True,
        'penalty': handler.penalty_start,
        'new_penalty': handler.penalty,
        'current_card': {'aces_high': False, 'rank': 'Ace', 'suit': 'Clubs'},
        'outcome': {
            'card': {'aces_high': False, 'rank': 'Ace', 'suit': 'Clubs'},
            'correct': True,
            'guess': 'Low',
            'penalty': 1,
            'player': {'active': True, 'username': 'mick'},
            'turn': 0
        },
        'player': {
            'username': p1.username,
            'active': True,
        }
    }
    assert mock_utils_send.broadcast == [
        expected_message
    ]
    assert handler.turn == 1
    assert handler.penalty == handler.penalty_start + handler.penalty_increment


@pytest.mark.asyncio
async def test_get_current_player(four_player_game_lobby):
    (handler, __websockets, players) = four_player_game_lobby
    (p1, p2, p3, __p4) = players

    handler.state = GameStates.PLAYING
    assert handler.get_current_player() == p1
    handler.turn += 1
    assert handler.get_current_player() == p2
    handler.turn += 1
    assert handler.get_current_player() == p3
    # p4 should be skipped because it's inactive
    handler.turn += 1
    assert handler.get_current_player() == p1
