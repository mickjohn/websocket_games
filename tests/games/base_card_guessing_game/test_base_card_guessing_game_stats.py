from websocketgames.games.players import Player
from websocketgames.games.base_card_guessing_game.stats import Stats, Outcome, _sort_dict, _sort_stat
from pytest import fixture


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
        Outcome(Player('mick', '123'), 0, 'Red', True, 1, 'A of Hearts', None),
        Outcome(Player('john', '456'), 1, 'Red', True, 2, '2 of Hearts', 'A of Hearts'),
        Outcome(Player('dracula', '789'), 2, 'Black', False, 3, '3 of Hearts', '2 of Hearts'),

        Outcome(Player('mick', '123'), 3, 'Red', True, 1, '4 of Hearts', '3 of Hearts'),
        Outcome(Player('john', '456'), 4, 'Red', False, 2, '5 of Hearts', '4 of Hearts'),
        Outcome(Player('dracula', '789'), 5, 'Black', False, 1, '6 of Hearts', '5 of Hearts'),

        Outcome(Player('mick', '123'), 6, 'Red', True, 1, '7 of Hearts', '6 of Hearts'),
        Outcome(Player('john', '456'), 7, 'Red', False, 2, '8 of Hearts', '7 of Hearts'),
        Outcome(Player('dracula', '789'), 8, 'Black', False, 3, '9 of Hearts', '8 of Hearts'),
    ]


def test_stats_update_correctly(outcomes):
    stats = Stats()
    for outcome in outcomes:
        stats.update(outcome)

    assert len(stats.correct) == 3
    assert len(stats.wrong) == 3
    assert len(stats.seconds_drank) == 3


def test_stats_sort_dict():
    data = {
        'a': 5,
        'b': 7,
        'c': 3,
        'd': 5,
    }

    expected = {
        'b': 7,
        'a': 5,
        'd': 5,
        'c': 3
    }

    assert _sort_dict(data) == expected


def test_stats_sort_stat():
    stats = Stats()
    stats.correct = {
        'mick': 10,
        'bob': 8,
        'antonio': 5,
        'lee': 8
    }
    expected = {
        1: {'score': 10, 'usernames': 'mick'},
        2: {'score': 8, 'usernames': 'bob, lee'},
        4: {'score': 5, 'usernames': 'antonio'},
    }
    assert _sort_stat(stats.correct) == expected


def test_stats_get_stats(outcomes):
    stats = Stats()
    for outcome in outcomes:
        stats.update(outcome)

    expected = {
        'best_players': {
            1: {'score': 3, 'usernames': 'mick'},
            2: {'score': 1, 'usernames': 'john'},
            3: {'score': 0, 'usernames': 'dracula'},
        },
        'worst_players': {
            1: {'score': 3, 'usernames': 'dracula'},
            2: {'score': 2, 'usernames': 'john'},
            3: {'score': 0, 'usernames': 'mick'},
        },
        'drunkest_players': {
            1: {'score': 7, 'usernames': 'dracula'},
            2: {'score': 4, 'usernames': 'john'},
            3: {'score': 0, 'usernames': 'mick'}
        },
    }

    assert stats.get_stats() == expected
