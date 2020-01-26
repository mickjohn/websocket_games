
type Suit = "Spades" | "Clubs" | "Hearts" | "Diamonds";
type SuitIcon = "♠" | "♣" | "♥" | "♦";
type Rank = "Ace" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | "10" | "Jack" | "Queen" | "King";

class Card {
    suit: Suit;
    suitIcon: SuitIcon;
    rank: Rank;

    constructor(suit: Suit, rank: Rank) {
        this.suit = suit;
        this.rank = rank;

        let suitIcon: SuitIcon;
        if (suit == "Clubs") {
            suitIcon = "♣";
        } else if (this.suit == "Diamonds") {
            suitIcon = "♦";
        } else if (this.suit == "Hearts") {
            suitIcon = "♥";
        } else {
            suitIcon = "♠";
        }
        this.suitIcon = suitIcon;
    }

    prettyPrint(): string {
        let suit: string;
        if (this.suit == "Clubs") {
            suit = "♣️";
        } else if (this.suit == "Diamonds") {
            suit = "♦️";
        } else if (this.suit == "Hearts") {
            suit = "♥️";
        } else {
            suit = "♠️";
        }
        return `${this.rank}${suit}`;
    }
}

export default Card;