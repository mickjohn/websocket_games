import Player from '../player';
import { GameHistoryItem } from '../GameHistory';
import Card from '../card';

class GuessOutcome {
    static msgtype = "GuessOutcome";

    player: Player;
    guess: string;
    correct: boolean;
    penalty: number;
    newPenalty: number;
    cardsLeft: number;
    turn: number;
    historyItem: GameHistoryItem;

    constructor(
        player: Player,
        guess: string,
        correct: boolean,
        penalty: number,
        newPenalty: number,
        cardsLeft: number,
        turn: number,
        historyItem: GameHistoryItem,
    ) {
        this.player = player;
        this.guess = guess;
        this.correct = correct;
        this.penalty = penalty;
        this.newPenalty = newPenalty;
        this.cardsLeft = cardsLeft;
        this.turn = turn;
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

        return new GuessOutcome(
            msg['player'],
            msg['guess'],
            msg['correct'],
            msg['penalty'],
            msg['new_penalty'],
            msg['cards_left'],
            msg['turn'],
            historyItem,
        );
    }

    createGameHistoryItem(): GameHistoryItem {
        return this.historyItem;
    }
}

export default GuessOutcome;