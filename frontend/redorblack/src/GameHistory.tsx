/*
A class for holding the guess and outcome history of the game
*/
export class GameHistoryItem {
    username: string;
    guess: string;
    correct: boolean;
    constructor(username: string, guess: string, correct: boolean) {
        this.username = username;
        this.guess = guess;
        this.correct = correct;
    }
}

export class GameHistory {
    max: number;
    _historyItems: Array<GameHistoryItem>;
    constructor(max: number) {
        this.max = max;
        this._historyItems = new Array();
    }

    addItem(item: GameHistoryItem) {
        if (this._historyItems.length >= this.max) {
            this._historyItems.pop();
        }
        this._historyItems.unshift(item);
    }

    items() {
        return this._historyItems;
    }
}