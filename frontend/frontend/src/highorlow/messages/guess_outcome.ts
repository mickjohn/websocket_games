import Player from '../../common/Player';
import { GameHistoryItem } from '../GameHistory';
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
    currentCard: Card;

    constructor(
        player: Player,
        guess: "High" | "Low",
        correct: boolean,
        penalty: number,
        newPenalty: number,
        cardsLeft: number,
        turn: number,
        currentCard: Card,
    ) {
        this.player = player;
        this.guess = guess;
        this.correct = correct;
        this.penalty = penalty;
        this.newPenalty = newPenalty;
        this.cardsLeft = cardsLeft;
        this.turn = turn;
        this.currentCard = currentCard;
    }

    static fromJson(msg: any): GuessOutcome | null {
        return new GuessOutcome(
            msg['player'],
            msg['guess'],
            msg['correct'],
            msg['penalty'],
            msg['new_penalty'],
            msg['cards_left'],
            msg['turn'],
            new Card(msg['current_card']['suit'], msg['current_card']['rank']),
        );
    }

    createGameHistoryItem(): GameHistoryItem {
        return new GameHistoryItem(
            this.player.username,
            this.guess,
            this.correct,
            this.penalty,
            this.turn,
        );
    }
}

export default GuessOutcome;