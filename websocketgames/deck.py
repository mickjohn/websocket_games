from random import shuffle as shuffle
from functools import total_ordering


class Deck():
    def __init__(self, shuffled=False, aces_high=False):
        self.shuffled = shuffled
        self.cards = self.__create_deck()
        self.aces_high = aces_high
        if shuffled:
            self.shuffle_cards()

    def shuffle_cards(self):
        shuffle(self.cards)

    def draw_card(self):
        return self.cards.pop()

    def __create_deck(self):
        ranks = ['Ace', '2', '3', '4', '5', '6', '7',
                 '8', '9', '10', 'Jack', 'Queen', 'King']
        suits = ['Diamonds', 'Hearts', 'Clubs', 'Spades']
        cards = []
        for suit in suits:
            for rank in ranks:
                cards.append(Card(rank, suit))
        return cards

    def __eq__(self, other):
        if isinstance(other, Deck):
            if len(other.cards) != len(self.cards):
                return False
            for (a, b) in zip(self.cards, other.cards):
                if a != b:
                    return False
            return True
        return False

    def __str__(self):
        return ''.join([f"{str(card)}\n" for card in self.cards])

    def __repr__(self):
        return str(self)


@total_ordering
class Card():
    _number_ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10']
    _face_ranks = ['Ace', 'Jack', 'Queen', 'King']
    _allowed_suits = ['Clubs', 'Diamonds', 'Hearts', 'Spades']
    _allowed_ranks = _number_ranks + _face_ranks
    _rank_values = {
        'Ace': 0,
        '1': 1,
        '2': 2,
        '3': 3,
        '4': 4,
        '5': 5,
        '6': 6,
        '7': 7,
        '8': 8,
        '9': 9,
        '10': 10,
        'Jack': 11,
        'Queen': 12,
        'King': 13,
    }

    def __init__(self, rank, suit, aces_high=False):
        if rank not in Card._allowed_ranks:
            raise Exception(f"Rank {rank} is not one of the allowed ranks")
        if suit not in Card._allowed_suits:
            raise Exception(f"Suit {suit} is not one of the allowed suits")

        self.aces_high = aces_high
        self.suit = suit
        self.rank = rank

    def get_colour(self):
        if self.suit in ['Clubs', 'Spades']:
            return 'Black'
        else:
            return 'Red'

    def _is_valid_operand(self, other):
        return (hasattr(other, "rank") and hasattr(other, "suit"))

    def __str__(self):
        return f"{self.rank} of {self.suit}"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.suit == other.suit and self.rank == other.rank
        return False

    def __lt__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        if not self == other and self.aces_high:
            return False
        return self._rank_values[self.rank] < self._rank_values[other.rank]
