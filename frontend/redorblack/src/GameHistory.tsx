/*
A class for holding the guess and outcome history of the game
*/
export class GameHistoryItem {
    username: string;
    guess: string;
    correct: boolean;
    penalty: number;
    turn: number;

    constructor(username: string, guess: string, correct: boolean, penalty: number, turn: number) {
        this.username = username;
        this.guess = guess;
        this.correct = correct;
        this.penalty = penalty;
        this.turn = turn;
    }

    public toString(): string {
        return JSON.stringify(this);
    }
}

export class GameHistory {
    max: number | undefined;
    _historyItems: Array<GameHistoryItem>;
    constructor(max?: number) {
        this.max = max;
        this._historyItems = new Array();
    }

    addItem(item: GameHistoryItem) {
        if (this.max !== undefined) {
            if (this._historyItems.length >= this.max) {
                this._historyItems.pop();
            }
        }
        this._historyItems.unshift(item);
    }

    items() {
        return this._historyItems;
    }
}