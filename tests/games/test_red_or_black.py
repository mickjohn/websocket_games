from websocketgames.games.red_or_black import RedOrBlack
from websocketgames.games.base_card_guessing_game.states import GameStates

from websocketgames.games.players import Player
from websocketgames import deck
from tests.games.game_test_utils import MockWebsocket, mock_utils_send

import pytest
from pytest import fixture


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
async def test_play_turn(mock_utils_send, four_player_game_lobby):
    (handler, websockets, players) = four_player_game_lobby
    (ws1, *_) = websockets
    (p1, *_) = players
    # Set cards to something we know
    handler.state = GameStates.PLAYING
    handler.turn_sleep_s = 0
    handler.deck.cards = [deck.Card('Ace', 'Clubs')] * 10

    # Guess correct answer
    msg = {'type': 'PlayTurn', 'guess': 'Black'}
    await handler.play_turn(ws1, msg)
    expected_message = {
        'type': 'GuessOutcome',
        'guess': 'Black',
        'cards_left': 9,
        'turn': 0,
        'correct': True,
        'penalty': handler.penalty_start,
        'new_penalty': handler.penalty,
        'outcome': {
            'card': {'aces_high': False, 'rank': 'Ace', 'suit': 'Clubs'},
            'faceup_card': None,
            'correct': True,
            'guess': 'Black',
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
