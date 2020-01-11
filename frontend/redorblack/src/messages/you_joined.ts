import GameState from '../utils/game_state';
import { GameHistory, GameHistoryItem } from '../GameHistory';
import { Stats, parseStats } from '../components/GameOver/game_over';
import Player from '../player';
import * as Game from '../components/Game/game';

class YouJoined {
    static msgtype = "YouJoined";
    state: GameState;
    player: Player;
    owner: Player;
    players: Map<string, Player>;
    history: GameHistory;
    stats: Stats | null;
    turn: number;
    order: Player[];

    constructor(
        state: GameState,
        player: Player,
        owner: Player,
        players: Map<string, Player>,
        history: GameHistory,
        stats: Stats | null,
        turn: number,
        order: Player[],
    ) {
        this.state = state;
        this.player = player;
        this.owner = owner;
        this.players = players;
        this.history = history;
        this.stats = stats;
        this.turn = turn;
        this.order = order;
    }

    static fromJson(msg: any): YouJoined | null {
        const gameState = msg['game_state'];
        const state: GameState = Game.parseState(msg['game_state']['state']);
        const player: Player = new Player(msg['player']['username'], msg['player']['active']);
        const owner: Player = new Player(gameState['owner']['username'], gameState['owner']['active']);
        const playersJson = gameState['players'];
        const historyJson = gameState['history'];
        const history = new GameHistory();
        const turn: number = gameState['turn'];
        const order: Player[] = gameState['order'];
        let stats: Stats | null = null;

        if (state === GameState.Finished) {
            stats = parseStats(msg['stats']);
        }

        for (let outcome of historyJson) {
            const histItem: GameHistoryItem = new GameHistoryItem(
                outcome['player']['username'],
                outcome['guess'],
                outcome['correct'],
                outcome['penalty'],
                outcome['turn'],
            );
            history.addItem(histItem);
        }

        const players: Map<string, Player> = new Map();
        for (let pj of playersJson) {
            let newPlayer = new Player(pj['username'], pj['active']);
            players.set(newPlayer.username, newPlayer);
        }

        return new YouJoined(
            state,
            player,
            owner,
            players,
            history,
            stats,
            turn,
            order,
        );
    }
}

export default YouJoined;