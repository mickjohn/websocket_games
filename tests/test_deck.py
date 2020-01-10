from websocketgames.deck import Deck, Card
import pytest


def test_can_create_deck():
    deck = Deck()
    assert len(deck.cards) == 52
    assert deck.cards[0] == Card('Ace', 'Diamonds')


def test_deck_equality_works():
    deck1 = Deck()
    deck2 = Deck()
    assert deck1 == deck2
    deck1.cards[0] = Card('Ace', 'Spades')
    assert deck1 != deck2


def test_shuffling_works():
    deck1 = Deck()
    deck2 = Deck(shuffled=True)
    assert deck1 != deck2


def test_draw_card():
    deck = Deck()
    assert deck.draw_card() == Card('King', 'Spades')
    assert len(deck.cards) == 51


def test_card_error_when_invalid_rank():
    with pytest.raises(Exception) as e:
        Card('Big King', 'Diamonds')
    assert str(e.value) == 'Rank Big King is not one of the allowed ranks'


def test_card_error_when_invalid_suit():
    with pytest.raises(Exception) as e:
        Card('Ace', 'The red ones')
    assert str(e.value) == 'Suit The red ones is not one of the allowed suits'


def test_card_comparing():
    assert Card('Ace', 'Clubs') < Card('4', 'Clubs')
    assert Card('Ace', 'Clubs', aces_high=True) > Card('4', 'Clubs')
    assert Card('6', 'Clubs') >= Card('6', 'Clubs')
