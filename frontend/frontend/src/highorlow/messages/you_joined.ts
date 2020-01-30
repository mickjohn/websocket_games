import GameState from '../utils/game_state';
import { GameHistory, GameHistoryItem } from '../../common/GameHistory';
import { Stats, parseStats } from '../components/GameOver/game_over';
import Player from '../../common/Player';
import * as Game from '../components/Game/game';
import Card from '../../common/Card';

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
    currentCard: Card;
    penalty: number;
    cardsLeft: number;

    constructor(
        state: GameState,
        player: Player,
        owner: Player,
        players: Map<string, Player>,
        history: GameHistory,
        stats: Stats | null,
        turn: number,
        order: Player[],
        currentCard: Card,
        penalty: number,
        cardsLeft: number,
    ) {
        this.state = state;
        this.player = player;
        this.owner = owner;
        this.players = players;
        this.history = history;
        this.stats = stats;
        this.turn = turn;
        this.order = order;
        this.currentCard = currentCard;
        this.penalty = penalty;
        this.cardsLeft = cardsLeft;
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
        const currentCard: Card = new Card(gameState['current_card']['suit'], gameState['current_card']['rank']);
        const penalty: number = gameState['penalty'];
        const cardsLeft: number = gameState['cards_left'];
        let stats: Stats | null = null;

        if (state === GameState.Finished) {
            stats = parseStats(msg['stats']);
        }

        for (let outcome of historyJson) {
            const histItem: GameHistoryItem = new GameHistoryItem(
                outcome['player'],
                outcome['guess'],
                outcome['correct'],
                outcome['penalty'],
                outcome['turn'],
                new Card(outcome['card']['suit'], outcome['card']['rank']),
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
            currentCard,
            penalty,
            cardsLeft,
        );
    }
}

export default YouJoined;