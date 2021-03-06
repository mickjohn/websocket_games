import Player from '../../common/Player';
import { GameHistoryItem } from '../../common/GameHistory';
import Card from '../../common/Card';

class GuessOutcome {
    static msgtype = "GuessOutcome";

    player: Player;
    guess: "High" | "Low";
    correct: boolean;
    penalty: number;
    newPenalty: number;
    cardsLeft: number;
    turn: number;
    currentCard: Card | undefined;
    historyItem: GameHistoryItem;

    constructor(
        player: Player,
        guess: "High" | "Low",
        correct: boolean,
        penalty: number,
        newPenalty: number,
        cardsLeft: number,
        turn: number,
        currentCard: Card | undefined,
        historyItem: GameHistoryItem,
    ) {
        this.player = player;
        this.guess = guess;
        this.correct = correct;
        this.penalty = penalty;
        this.newPenalty = newPenalty;
        this.cardsLeft = cardsLeft;
        this.turn = turn;
        this.currentCard = currentCard;
        this.historyItem = historyItem;
    }

    static fromJson(msg: any): GuessOutcome | null {
        let card = new Card(msg['outcome']['card']['suit'], msg['outcome']['card']['rank']);
        const historyItem = new GameHistoryItem(
            msg['player'],
            msg['guess'],
            msg['correct'],
            msg['penalty'],
            msg['turn'],
            card,
        );

        let outcomeItem = msg['outcome'];
        let currentCard: Card | undefined;
        if (outcomeItem['card'] == null) {
            currentCard = undefined;
        } else {
            currentCard = new Card(outcomeItem['card']['suit'], outcomeItem['card']['rank']);
        }

        return new GuessOutcome(
            msg['player'],
            msg['guess'],
            msg['correct'],
            msg['penalty'],
            msg['new_penalty'],
            msg['cards_left'],
            msg['turn'],
            currentCard,
            historyItem,
        );
    }
}

export default GuessOutcome;