import Player from '../player';
import { GameHistoryItem } from '../GameHistory';

class GuessOutcome {
    static msgtype = "GuessOutcome";

    player: Player;
    guess: string;
    correct: boolean;
    penalty: number;
    newPenalty: number;
    cardsLeft: number;
    turn: number;

    constructor(
        player: Player,
        guess: string,
        correct: boolean,
        penalty: number,
        newPenalty: number,
        cardsLeft: number,
        turn: number
    ) {
        this.player = player;
        this.guess = guess;
        this.correct = correct;
        this.penalty = penalty;
        this.newPenalty = newPenalty;
        this.cardsLeft = cardsLeft;
        this.turn = turn;
    }

    static fromJson(msg: any): GuessOutcome | null {
        return new GuessOutcome(
            msg['player'],
            msg['guess'],
            msg['correct'],
            msg['penalty'],
            msg['new_penalty'],
            msg['cards_left'],
            msg['turn']
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