import Card from "./Card";
import Player from "./Player";

/*
A class for holding the guess and outcome history of the game
*/
export class GameHistoryItem {
    player: Player;
    guess: string;
    correct: boolean;
    penalty: number;
    turn: number;
    card: Card;

    constructor(player: Player, guess: string, correct: boolean, penalty: number, turn: number, card: Card) {
        this.player = player;
        this.guess = guess;
        this.correct = correct;
        this.penalty = penalty;
        this.turn = turn;
        this.card = card;
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
        this._historyItems = [];
    }

    addItem(item: GameHistoryItem) {
        if (this.max !== undefined) {
            if (this._historyItems.length >= this.max) {
                this._historyItems.pop();
            }
        }
        this._historyItems.unshift(item);
    }

    addItems(items: GameHistoryItem[]) {
        this._historyItems.concat(items);
    }

    items() {
        return this._historyItems;
    }
}