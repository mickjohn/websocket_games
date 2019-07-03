from websocketgames.games import red_or_black
from websocketgames.games.red_or_black import RedOrBlackGame, GameStates
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
