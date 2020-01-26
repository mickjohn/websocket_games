import {Stats, parseStats} from '../components/GameOver/game_over';

class GameFinished {
    static msgtype = "GameFinished";
    stats: Stats;

    constructor(stats: Stats) {
        this.stats = stats;
     }

    static fromJson(msg: any): GameFinished | null {
        const stats = parseStats(msg['stats']);
        return new GameFinished(stats);
    }
}

export default GameFinished;