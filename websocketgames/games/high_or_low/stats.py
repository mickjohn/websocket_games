from collections import defaultdict
from itertools import groupby


class Outcome:

    def __init__(self, player, turn, guess, correct, card, penalty):
        self.player = player
        self.turn = turn
        self.guess = guess
        self.correct = correct
        self.card = card
        self.penalty = penalty


class Stats:

    def __init__(self):
        self.outcomes = []
        self.correct = defaultdict(int)
        self.wrong = defaultdict(int)
        self.seconds_drank = defaultdict(int)

    def update(self, outcome):
        self.outcomes.append(outcome)
        username = outcome.player.username
        if outcome.correct:
            self.correct[username] += 1
            self.wrong[username] += 0
            self.seconds_drank[username] += 0
        else:
            self.correct[username] += 0
            self.wrong[username] += 1
            self.seconds_drank[username] += outcome.penalty

    def get_stats(self):
        return {
            'best_players': _sort_stat(self.correct),
            'worst_players': _sort_stat(self.wrong),
            'drunkest_players': _sort_stat(self.seconds_drank),
        }


def _sort_stat(data):
    sorted_data = _sort_dict(data)
    retval = {}
    place = 1
    for score, players in groupby(sorted_data.items(), key=lambda item: item[1]):
        usernames = [x[0] for x in list(players)]
        retval[place] = {'score': score, 'usernames': ', '.join(usernames)}
        place += len(usernames)
    return retval


def _sort_dict(data):
    def sortfunc(item):
        return item[1]*-1
    return {k: v for k, v in sorted(data.items(), key=sortfunc)}
