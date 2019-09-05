
export class Game {
    path: string;
    displayName: string;
    checksum: 0;

    constructor(path: string, displayName: string, checksum: number) {
        this.path = path;
        this.displayName = displayName;
        this.checksum = 0;
    }

    public toString = (): string => {
        return this.displayName;
    }
}

export const games: Array<Game> = [
    new Game('redorblack', 'Red or Black', 0),
]

export let gameTable: Map<number, Game> = new Map();

games.forEach(game => {
    gameTable.set(game.checksum, game);
});

export default Game;