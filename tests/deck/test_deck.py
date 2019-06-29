from websocketgames.deck import Deck, Card

def test_can_create_deck():
    deck = Deck()
    assert len(deck.cards) == 52
    assert deck.cards[0] == Card('Ace', 'Diamonds')

def test_deck_equality_works():
    deck1 = Deck()
    deck2 = Deck()
    assert deck1 == deck2
    deck1.cards[0] = Card('0', '0')
    assert deck1 != deck2

def test_shuffling_works():
    deck1 = Deck()
    deck2 = Deck(shuffled=True)
    assert deck1 != deck2

def test_draw_card():
    deck = Deck()
    assert deck.draw_card() == Card('King', 'Spades')
    assert len(deck.cards) == 51