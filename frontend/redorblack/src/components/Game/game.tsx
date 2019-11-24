import React from 'react';
import config from '../../config';
import Guess from '../../utils/guess';
import UrlParams from '../../utils/url_params';
import GameState from '../../utils/game_state';
import './game.css';
import { GameHistory, GameHistoryItem } from '../../GameHistory';

// Components:
import ConnStatus from '../ConnStatus/conn_status';
import Lobby from '../Lobby/lobby';
import GameScreen from '../GameScreen/game_screen';
import Player from '../../player';
import HistoryBox from '../HistoryBox/history_box';
import PenaltyBox from '../PenaltyBox/penalty_box';
import CorrectBox from '../CorrectBox/correct_box';
import DotsThrobber from '../DotsThrobber/dots_throbber';
import GameInfo from '../GameInfo/game_info';


function parseState(s: string) {
    console.debug(`state = ${s}`);
    if (s === 'PLAYING') {
        return GameState.Playing;
    } else if (s === 'LOBBY') {
        return GameState.Lobby;
    } else if (s === 'FINISHED') {
        return GameState.Finished;
    }
    return GameState.NoState;
}

interface State {
    // Websocket connection status
    websocketStatus: number;

    // The websocket connection to the game server
    websocket: WebSocket;

    // The UID used to join the game
    user_id: string;

    // The game code
    game_id: string;

    // Map of username -> Player
    players: Map<string, Player>;

    // The current player of the game
    player: Player | undefined;

    // The owner is the first player to join the game.
    // Only the owner can start the game
    owner: Player | undefined;

    // The playing state of the game, e.g. lobby, finished
    game_state: GameState;

    // A class containing the required URL params 
    url_params: UrlParams;

    // Game turn number
    turn: number;

    // The outcomes from the turns
    game_history: GameHistory;

    // The penalty to drink
    penalty: number | null;

    // If true show 'your correct box'
    show_correct: boolean;

    // Waiting for guess result
    waiting_for_result: boolean;

    // Array of players in order of thier turn
    order: Array<Player>;

    // What to do when start game clicked
    start_game_handler: (event: any) => void;

    // What to do when guess button is clicked
    makeGuessHandler: (guess: Guess) => void;

    // Function to clear the penalty.
    clearPenaltyHandler: () => void;

    // Function to cleat the correct box.
    clearCorrectCallback: () => void;
}

interface Props { }

class Game extends React.Component<Props, State>   {
    _ismounted: boolean;
    _conn_status: string;

    constructor(props: Props) {
        super(props);

        if (!this.hasUrlParams()) {
            this.redirect();
        }

        let params: UrlParams = this.getUrlParams();

        this._ismounted = false;
        this._conn_status = "not connected";
        let websocket: WebSocket = this.createWebsocket(`wss://${config.websocketUrl}/game_${params.game_id}`);
        this.state = {
            websocketStatus: WebSocket.CLOSED,
            websocket: websocket,
            user_id: params.user_id,
            game_id: params.game_id,
            players: new Map(),
            game_history: new GameHistory(5),
            player: undefined,
            show_correct: false,
            owner: undefined,
            game_state: GameState.NoState,
            start_game_handler: this.startGameCallback.bind(this),
            makeGuessHandler: this.makeGuessCallback.bind(this),
            clearPenaltyHandler: this.clearPenaltyHandler.bind(this),
            clearCorrectCallback: this.clearCorrectCallback.bind(this),
            url_params: params,
            turn: 0,
            penalty: null,
            waiting_for_result: false,
            order: [],
        };

        websocket.onopen = () => {
            this.setState({ websocketStatus: websocket.readyState });
            this.joinGame();
        }

    }

    hasUrlParams(): boolean {
        let params = new URLSearchParams(document.location.search.substring(1));
        return params.has("uid") && params.has("game_id");
    }

    getUrlParams(): UrlParams {
        let params = new URLSearchParams(document.location.search.substring(1));
        let uid: string = params.get("uid") || '';
        let game_id: string = params.get("game_id") || '';
        return new UrlParams(uid, game_id);
    }

    websocketIsConnected(): boolean {
        return this.state.websocket.readyState === WebSocket.OPEN;
    }

    redirect(): void {
        let location: Location = window.location;
        let protocol: string = location.protocol;
        let url: string = `${protocol}//${config.baseUrl}/index.html`;
        console.debug(`Redirecting to ${url}`);
        window.location.href = url;
    }

    componentDidMount(): void {
        this._ismounted = true;
    }

    componentWillUnmount(): void {
        this._ismounted = false;
    }

    handleMessage(msg: any): void {
        let obj = JSON.parse(msg);
        console.debug(obj);
        if (obj['type'] === null) {
            console.error("Message has no 'type'");
            return;
        }

        if (obj['type'] === 'YouJoined') {
            /*************/
            /* YouJoined */
            /*************/
            console.debug("You have joined the game");
            const gameState = obj['game_state'];
            const player = new Player(obj['player']['username'], obj['player']['active']);
            const owner = new Player(gameState['owner']['username'], gameState['owner']['active']);
            const playersJson = gameState['players'];
            const history = gameState['shortend_history'];

            const tempHist: GameHistory = this.state.game_history;
            for (let outcome of history) {
                const histItem: GameHistoryItem = new GameHistoryItem(
                    outcome['player']['username'],
                    outcome['guess'],
                    outcome['correct'],
                    outcome['penalty']
                );
                tempHist.addItem(histItem);
            }

            const players: Map<string, Player> = new Map();
            for (let pj of playersJson) {
                let newPlayer = new Player(pj['username'], pj['active']);
                players.set(newPlayer.username, newPlayer);
            }

            this.setState({
                player: player,
                owner: owner,
                players: players,
                game_state: parseState(gameState['state']),
                turn: gameState['turn'],
                order: gameState['order'],
                game_history: tempHist,
            });
        } else if (obj['type'] === 'PlayerAdded') {
            /***************/
            /* PlayerAdded */
            /***************/
            console.debug("Adding new player");
            const new_player = new Player(obj['player']['username'], obj['player']['active']);
            const map = this.state.players;
            map.set(new_player.username, new_player);
            this.setState({ players: map });
        } else if (obj['type'] === 'PlayerDisconnected') {
            /**********************/
            /* PlayerDisconnected */
            /**********************/
            console.debug('Player disconnected');
            const username = obj['player']['username'];
            const map = this.state.players;
            map.delete(username);
            this.setState({ players: map });
        } else if (obj['type'] === 'GameStarted') {
            /***************/
            /* GameStarted */
            /***************/
            console.debug('game starting');
            this.setState({ game_state: GameState.Playing })
        } else if (obj['type'] === 'NewOwner') {
            /************/
            /* NewOwner */
            /************/
            console.info('NewOwner: Updating Owner');
            const owner = new Player(obj['owner']['username'], obj['owner']['active'])
            this.setState({ owner: owner });
        } else if (obj['type'] === 'OrderChanged') {
            /****************/
            /* OrderChanged */
            /****************/
            console.info("OrderChanged: updating order");
            const order = obj['order'];
            this.setState({ order: order });
        } else if (obj['type'] === 'GuessOutcome') {
            /****************/
            /* GuessOutcome */
            /****************/
            const index: number = this.state.turn % this.state.order.length;
            const currentPlayer = this.state.order[index];
            let show_correct: boolean = false;
            if (this.state.player !== undefined) {
                if (this.state.player.username == currentPlayer.username) {
                    if (obj['correct'] === true) {
                        // Player is right!
                        show_correct = true;
                    } else {
                        // Player is wrong!
                    }
                }
            }

            const item = new GameHistoryItem(
                obj['player']['username'],
                obj['guess'],
                obj['correct'],
                obj['penalty']
            );

            const items = this.state.game_history;
            items.addItem(item);
            // Update the turn number and history
            // Don't accidently clear the penalty
            let penalty: number | null = this.state.penalty;
            if (this.state.penalty === null) {
                console.log(`setting penalty to ${this.getPenaltyForThisPlayer()}`);
                penalty = this.getPenaltyForThisPlayer();
            }

            this.setState({
                turn: obj['turn'],
                game_history: items,
                penalty: penalty,
                show_correct: show_correct,
                waiting_for_result: false,
            });

        } else if (obj['type'] === 'Error') {
            /**********/
            /* Errors */
            /**********/
            if (obj['error_type'] === 'GameNotFound') {
                this.redirect();
            }

        } else {
            console.warn(`Unidentifed message type '${obj['type']}'`);
        }
    }

    createWebsocket(url: string): WebSocket {
        console.info("Creating websocket connection");
        let websocket: WebSocket = new WebSocket(url);
        websocket.onclose = () => this.setState({ websocketStatus: websocket.readyState });
        websocket.onerror = () => this.setState({ websocketStatus: websocket.readyState });
        websocket.onmessage = (ev) => this.handleMessage(ev.data);
        return websocket;
    }

    joinGame(): void {
        let msg: any = {
            "type": "Activate",
            "user_id": this.state.user_id,
        }
        this.state.websocket.send(JSON.stringify(msg));
    }

    getPenaltyForThisPlayer(): number | null {
        if (this.state.player === undefined) {
            return null;
        }
        const hist = this.state.game_history;
        if (hist.items().length === 0) {
            return null;
        }
        const item = hist.items()[0];
        console.log(`hist item = ${item}`);
        if (item.username === this.state.player.username) {
            if (!item.correct) {
                return item.penalty;
            }
        }
        return null;
    }

    render() {
        let stateElement: JSX.Element | null = null;

        if (this.state.game_state === GameState.NoState) {
            stateElement = <p>no state</p>;
        } else if (this.state.game_state === GameState.Playing) {
            if (
                this.state.player !== undefined
                && this.state.penalty === null
                && !this.state.waiting_for_result
                && !this.state.show_correct
            ) {
                stateElement = (
                    <GameScreen
                        turn={this.state.turn}
                        order={this.state.order}
                        makeGuessCallback={this.state.makeGuessHandler}
                        player={this.state.player}
                        game_history={this.state.game_history}
                    />
                );
            } else {
                stateElement = null;
            }
        } else if (this.state.game_state === GameState.Finished) {
            stateElement = <p>Finished</p>;
        }

        let lobby: JSX.Element;
        if (this.state.game_state === GameState.Lobby && this.websocketIsConnected()) {
            lobby = (
                <Lobby
                    players={this.state.players}
                    owner={this.state.owner}
                    player={this.state.player}
                    onClick={this.state.start_game_handler}
                />
            );
        } else {
            lobby = <span></span>;
        }

        return (
            <div>
                <header className="GameHeader">Red or Black</header>
                <div className="GameScreen">
                    <ConnStatus status={this.state.websocketStatus} />
                    <GameInfo
                        turn={this.state.turn}
                        order={this.state.order}
                        player={this.state.player}
                    />
                    <div className="InteractiveContent">
                        {stateElement}
                        <PenaltyBox
                            penalty={this.state.penalty}
                            clearPenaltyCallback={this.state.clearPenaltyHandler}
                        />
                        <CorrectBox
                            show_box={this.state.show_correct}
                            clearCorrectCallback={this.state.clearCorrectCallback}
                        />
                        <DotsThrobber show={this.state.waiting_for_result} />
                    </div>
                    {lobby}
                    <HistoryBox game_history={this.state.game_history} />
                </div>
            </div>
        );
    }

    /*************/
    /* Callbacks */
    /*************/
    startGameCallback() {
        console.debug('Start game clicked');
        let urlParams = this.state.url_params;
        const msg = {
            'type': 'StartGame',
            'user_id': urlParams.user_id,
        };
        this.state.websocket.send(JSON.stringify(msg));
    }

    makeGuessCallback(guess: Guess) {
        if (this.state.player !== undefined && this.state.order.length > 0) {
            const p = this.state.player;
            let currentPlayer: Player = this.state.order[this.state.turn % this.state.order.length];
            if (p.username === currentPlayer.username) {
                let msg;
                if (guess === Guess.Black) {
                    msg = { 'guess': 'Black', 'type': 'PlayTurn' };
                } else {
                    msg = { 'guess': 'Red', 'type': 'PlayTurn' };
                }
                this.state.websocket.send(JSON.stringify(msg));
                this.setState({ waiting_for_result: true });
            }
        }
    }

    clearPenaltyHandler() {
        window.navigator.vibrate(100);
        this.setState({ penalty: null });
    }

    clearCorrectCallback() {
        window.navigator.vibrate(100);
        this.setState({ show_correct: false });
    }

    /*****************/
    /* End Callbacks */
    /*****************/
}



export default Game;
