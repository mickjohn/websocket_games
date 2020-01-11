class GameStarted {
    static msgtype = "GameStarted";
    constructor() { }

    static fromJson(_msg: any): GameStarted | null {
        return new GameStarted();
    }
}

export default GameStarted;