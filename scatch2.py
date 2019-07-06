import itertools
from collections import defaultdict

def get_number_suffix(n):
    if n in [11, 12]:
        return 'th'
    elif n % 10 == 1:
        return 'st'
    elif n % 10 == 2:
        return 'nd'
    elif n % 10 == 3:
        return 'rd'
    else:
        return 'th'

usernames = [
    'mickjohn',
    'mark',
    'arnold',
    'jenson',
    'caroline',
    'mickjohn',
    'arnold',
    'jenson',
    'mickjohn',
    'mark',
    'caroline',
    'caroline',
    'mickjohn',
    'peter',
    'peter',
    'peter',
]

print(f"usernames = {usernames}")
usernames = sorted(usernames)

print(f"sorted usernames = {usernames}")

lowest_to_highest_scorers = []
score_dict = defaultdict(list)
for k,v in itertools.groupby(usernames):
    print(f"k = {k}")
    print(f"v = {list(v)}")
    score = len(list(v))
    score_dict[score].append(k)
    lowest_to_highest_scorers.append((k, score))

print(lowest_to_highest_scorers)
u,s = lowest_to_highest_scorers[-1]
print(f"{u}:{s}")

print(f"score dict = {score_dict}")

scores = sorted(list(score_dict.keys()))
scores.reverse()

place = 1
for score in scores:
    names = '\n     '.join(score_dict[score])
    print(f"{place}{get_number_suffix(place)}: {names}")
    place += len(score_dict[score])
