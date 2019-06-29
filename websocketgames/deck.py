from random import shuffle as shuffle


class Deck():
    def __init__(self, shuffled=False):
        self.shuffled = shuffled
        self.cards = self.__create_deck()
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


class Card():
    def __init__(self, rank, suit):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank} of {self.suit}"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.suit == other.suit and self.rank == other.rank
        return False
