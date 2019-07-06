from websocketgames.games import red_or_black
from websocketgames.games.red_or_black import RedOrBlackGame, GameStates, Player
from websocketgames.deck import Card
import pytest


def test_add_user():
    game = RedOrBlackGame('AAAA')
    uid = game.add_player('mickjohn')
    assert uid
    assert len(game.usernames_map) == 1
    assert len(game.id_map) == 1
    p = game.usernames_map['mickjohn']
    assert p.username == 'mickjohn'
    assert game.order[0].username == 'mickjohn'


def test_add_user_cant_have_duplicate_usernames():
    game = RedOrBlackGame('AAAA')
    game.add_player('mickjohn')
    with pytest.raises(red_or_black.UserAlreadyExists) as e:
        game.add_player('mickjohn')
    assert "User mickjohn already exists in AAAA" in str(e.value)


def test_start_game():
    game = RedOrBlackGame('AAAA')
    owner_id = game.add_player('mickjohn')
    game.add_player('qwert')
    game.start_game(owner_id)
    assert game.is_playing()


def test_start_game_raises_error_if_user_doesnt_exist():
    game = RedOrBlackGame('AAAA')
    with pytest.raises(red_or_black.UserDoesNotExist) as e:
        game.start_game('id')
    assert "No id id in game AAAA" == str(e.value)


def test_start_game_only_owner_can_start():
    game = RedOrBlackGame('AAAA')
    __owner_id = game.add_player('mickjohn')
    other_id = game.add_player('qwert')
    with pytest.raises(red_or_black.UserNotAllowedToStart) as e:
        game.start_game(other_id)
    assert "User qwert is not allowed to start the game" == str(e.value)


def test_can_play_turn():
    game = RedOrBlackGame('AAAA')
    player1 = game.add_player('mickjohn')
    game.add_player('player2')
    game.start_game(player1)
    assert game.can_play_turn(player1)


def test_can_play_turn_fails_when_not_players_turn():
    game = RedOrBlackGame('AAAA')
    player1 = game.add_player('mickjohn')
    player2 = game.add_player('player2')
    game.start_game(player1)
    assert game.can_play_turn(player1)
    with pytest.raises(red_or_black.NotPlayersTurn) as e:
        game.can_play_turn(player2)
    assert "It's not the go of player2, it's mickjohn" == str(e.value)


def test_can_play_turn_fails_game_is_not_in_progress():
    game = RedOrBlackGame('AAAA')
    game.add_player('mickjohn')
    with pytest.raises(red_or_black.WrongStateException) as e:
        game.can_play_turn('')
    assert "Game is not in playing state" == str(e.value)


def test_play_turn():
    game = RedOrBlackGame('AAAA')
    player1 = game.add_player('mickjohn')
    player2 = game.add_player('player2')
    game.start_game(player1)
    assert isinstance(game.play_turn(player1, 'Black'), bool)
    assert isinstance(game.play_turn(player2, 'Red'), bool)
    assert isinstance(game.play_turn(player1, 'Red'), bool)
    assert isinstance(game.play_turn(player2, 'Black'), bool)
    print(game.stats['outcomes'])
    assert len(game.stats['outcomes']) == 4
    assert game.stats['outcomes'][1]['player'].username == 'mickjohn'
    assert game.stats['outcomes'][2]['player'].username == 'player2'


def test_play_turn_game_ends_when_deck_is_exhausted():
    game = RedOrBlackGame('AAAA')
    player1 = game.add_player('mickjohn')
    game.start_game(player1)
    del(game.deck.cards[1:])
    game.play_turn(player1, 'Black')
    assert game.state == GameStates.FINISHED


def test_end_game():
    game = RedOrBlackGame('AAAA')
    game.end_game()
    assert game.state == GameStates.FINISHED


def test_restart_game():
    game = RedOrBlackGame('AAAA')
    player1 = game.add_player('mickjohn')
    game.start_game(player1)
    del(game.deck.cards[1:])
    game.play_turn(player1, 'Black')
    assert game.state == GameStates.FINISHED
    game.restart_game(player1)
    assert game.state == GameStates.PLAYING
    assert game.turn == 0
    assert len(game.stats['outcomes']) == 0
    assert len(game.deck.cards) == 52


def test_present_stats():
    stats = {
        'outcomes': {
            1: {
                'player': Player('mickjohn', ''),
                'turn': 1,
                'guess': 'Red',
                'outcome': True,
                'card': Card('1', 'Clubs'),
            },
            2: {
                'player': Player('michael', ''),
                'turn': 2,
                'guess': 'Red',
                'outcome': False,
                'card': Card('1', 'Clubs'),
            },
            3: {
                'player': Player('john', ''),
                'turn': 3,
                'guess': 'Black',
                'outcome': False,
                'card': Card('1', 'Clubs'),
            },
            4: {
                'player': Player('mickjohn', ''),
                'turn': 4,
                'guess': 'Red',
                'outcome': True,
                'card': Card('1', 'Clubs'),
            },
        }
    }
    game = RedOrBlackGame('AAAA')
    game.stats = stats
    [game.add_player(n) for n in ['mickjohn', 'michael', 'john']]
    pretty_stats = game.present_stats()
    assert pretty_stats['wrong_guesses'] == 2
    assert pretty_stats['right_guesses'] == 2
    assert pretty_stats['red'] == 3
    assert pretty_stats['black'] == 1
    assert pretty_stats['turns'] == 4
    assert pretty_stats['scores'][0] == (0, ['john', 'michael'])
    assert pretty_stats['scores'][1] == (2, ['mickjohn'])


def test_get_ranks():
    game = RedOrBlackGame('AAAA')
    players = ['mick', 'jane', 'dave', 'peter', 'noscore', 'noscore2']
    for p in players:
        game.add_player(p)

    correct_guesses = ['mick', 'jane', 'mick',
                       'jane', 'dave', 'dave', 'mick', 'peter']

    expected = [
        (0, ['noscore', 'noscore2']),
        (1, ['peter']),
        (2, ['dave', 'jane']),
        (3, ['mick']),
    ]
    assert game._get_ranks(correct_guesses) == expected
