import React from 'react';
import config from '../config';
import Guess from '../utils/guess';
import UrlParams from '../utils/url_params';
import GameState from '../utils/game_state';
import './Game.css';

// Components:
import ConnStatus from '../connstatus/ConnStatus';
import Lobby from '../lobby/lobby';
import GameScreen from '../game_screen/GameScreen';
import Player from '../player';


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

    // Array of players in order of thier turn
    order: Array<Player>;

    // What to do when start game clicked
    start_game_handler: (event: any) => void;

    makeGuessHandler: (guess: Guess) => void;
}

interface Props { }

/*
check the url for parameters and try to join
otherwise, redirect
*/

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
        let websocket: WebSocket = this.createWebsocket(`ws://${config.websocketUrl}/game_${params.game_id}`);
        this.state = {
            websocketStatus: WebSocket.CLOSED,
            websocket: websocket,
            user_id: params.user_id,
            game_id: params.game_id,
            players: new Map(),
            player: undefined,
            owner: undefined,
            game_state: GameState.NoState,
            start_game_handler: this.startGameCallback.bind(this),
            makeGuessHandler: this.makeGuessCallback.bind(this),
            url_params: params,
            turn: 0,
            order: [],
        };

        websocket.onopen = () => {
            this.setState({ websocketStatus: websocket.readyState });
            this.joinGame();
        }

    }

    hasUrlParams() {
        let params = new URLSearchParams(document.location.search.substring(1));
        return params.has("uid") && params.has("game_id");
    }

    getUrlParams() {
        let params = new URLSearchParams(document.location.search.substring(1));
        let uid: string = params.get("uid") || '';
        let game_id: string = params.get("game_id") || '';
        return new UrlParams(uid, game_id);
    }

    websocketIsConnected(): boolean {
        return this.state.websocket.readyState === WebSocket.OPEN;
    }

    redirect() {
        let location: Location = window.location;
        let protocol: string = location.protocol;
        let url: string = `${protocol}://${config.baseUrl}/index.html`;
        console.debug(`Redirecting to ${url}`);
        window.location.href = url;
    }

    componentDidMount() {
        this._ismounted = true;
    }

    componentWillUnmount() {
        this._ismounted = false;
    }

    handleMessage(msg: any) {
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
            if (this.state.player !== undefined) {
                if (this.state.player.username == currentPlayer.username) {
                    if (obj['correct'] == true) {
                        alert('Correct guess!');
                    } else {
                        alert('Wrong guess!');
                    }
                }
            }
            // Update the turn number
            this.setState({ turn: obj['turn'] });
        } else {
            console.warn(`Unidentifed message type '${obj['type']}'`);
        }
    }

    createWebsocket(url: string) {
        console.info("Creating websocket connection");
        let websocket: WebSocket = new WebSocket(url);
        websocket.onclose = () => this.setState({ websocketStatus: websocket.readyState });
        websocket.onerror = () => this.setState({ websocketStatus: websocket.readyState });
        websocket.onmessage = (ev) => this.handleMessage(ev.data);
        return websocket;
    }

    joinGame() {
        let msg: any = {
            "type": "Activate",
            "user_id": this.state.user_id,
        }
        this.state.websocket.send(JSON.stringify(msg));
    }

    render() {
        let stateElement: JSX.Element = <span></span>;

        if (this.state.game_state === GameState.NoState) {
            stateElement = <p>no state</p>;
        } else if (this.state.game_state === GameState.Playing) {
            if (this.state.player !== undefined) {
                stateElement = (
                    <GameScreen
                        turn={this.state.turn}
                        order={this.state.order}
                        makeGuessCallback={this.state.makeGuessHandler}
                        player={this.state.player}
                    />
                );
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
                <ConnStatus status={this.state.websocketStatus} />
                {lobby}
                {stateElement}
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
                    console.debug('Black guess clicked');
                } else {
                    msg = { 'guess': 'Red', 'type': 'PlayTurn' };
                    console.debug('Red guess clicked');
                }
                this.state.websocket.send(JSON.stringify(msg));
            } else {
                console.log("It's not your turn")
            }
        }
    }
}



export default Game;
