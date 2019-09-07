import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import ConnStatus from './connstatus/ConnStatus';
import Lobby from './lobby/lobby';
import GameScreen from './game_screen/game_screen';
import Player from './player';
import * as serviceWorker from './serviceWorker';
import config from './config';
import Game from './game/Game';

// enum GameProgressState {
//     Playing,
//     Lobby,
//     Finished,
//     NoState,
// }

// enum Guess {
//     Red,
//     Black,
// }

// function parseState(s: string) {
//     console.debug(`state = ${s}`);
//     if (s === 'PLAYING') {
//         return GameProgressState.Playing;
//     } else if (s === 'LOBBY') {
//         return GameProgressState.Lobby;
//     } else if (s === 'FINISHED') {
//         return GameProgressState.Finished;
//     }
//     return GameProgressState.NoState;
// }

// interface State {
//     // Websocket connection status
//     status: string;

//     // The websocket connection to the game server
//     websocket: WebSocket;

//     // The UID used to join the game
//     user_id: string;

//     // The game code
//     game_id: string;

//     // Map of username -> Player
//     players: Map<string, Player>;

//     // The current player of the game
//     player: Player | undefined;

//     // The owner is the first player to join the game.
//     // Only the owner can start the game
//     owner: Player | undefined;

//     // The playing state of the game, e.g. lobby, finished
//     game_state: GameProgressState;

//     // A class containing the required URL params 
//     url_params: UrlParams;

//     // Game turn number
//     turn: number;

//     // Array of players in order of thier turn
//     order: Array<Player>;

//     // What to do when start game clicked
//     start_game_handler: (event: any) => void;

//     makeGuessHandler: (guess: Guess) => void;
// }

// interface Props { }

// class UrlParams {
//     user_id: string;
//     game_id: string;

//     constructor(user_id: string, game_id: string) {
//         this.user_id = user_id;
//         this.game_id = game_id;
//     }
// }

// /*
// check the url for parameters and try to join
// otherwise, redirect
// */

// class Game extends React.Component<Props, State>   {
//     _ismounted: boolean;
//     _conn_status: string;

//     constructor(props: Props) {
//         super(props);

//         if (!this.hasUrlParams()) {
//             this.redirect();
//         }

//         let params: UrlParams = this.getUrlParams();

//         this._ismounted = false;
//         this._conn_status = "not connected";
//         let websocket: WebSocket = this.createWebsocket(`ws://${config.websocketUrl}/redorblack`);
//         this.state = {
//             status: this._conn_status,
//             websocket: websocket,
//             user_id: params.user_id,
//             game_id: params.game_id,
//             players: new Map(),
//             player: undefined,
//             owner: undefined,
//             game_state: GameProgressState.NoState,
//             start_game_handler: this.startGameCallback.bind(this),
//             makeGuessHandler: this.makeGuessCallback.bind(this),
//             url_params: params,
//             turn: 0,
//             order: [],
//         };

//         websocket.onopen = () => {
//             this.updateConnectionState();
//             this.joinGame();
//         }

//     }

//     hasUrlParams() {
//         let params = new URLSearchParams(document.location.search.substring(1));
//         return params.has("uid") && params.has("game_id");
//     }

//     getUrlParams() {
//         let params = new URLSearchParams(document.location.search.substring(1));
//         let uid: string = params.get("uid") || '';
//         let game_id: string = params.get("game_id") || '';
//         return new UrlParams(uid, game_id);
//     }

//     redirect() {
//         // let location: Location = window.location;
//         // let protocol: string = location.protocol;
//         // let host: string = location.host;
//         // let url: string = `${protocol}//${host}/`;
//         let url: string = `http://${config.websocketUrl}/index.html`;
//         window.location.href = url;
//     }

//     componentDidMount() {
//         this._ismounted = true;
//         this.setState({ status: this._conn_status });
//     }

//     componentWillUnmount() {
//         this._ismounted = false;
//     }

//     getConnectionStatus() {
//         if (this.state.websocket !== null) {
//             let ws = this.state.websocket;
//             if (ws.readyState === WebSocket.OPEN) {
//                 return "connected";
//             } else if (ws.readyState === WebSocket.CLOSED) {
//                 return "not connected";
//             } else if (ws.readyState === WebSocket.CONNECTING) {
//                 return "connecting";
//             } else if (ws.readyState === WebSocket.CLOSING) {
//                 return "closing";
//             } else {
//                 return "undefined";
//             }
//         } else {
//             return "not connected";
//         }
//     }

//     updateConnectionState() {
//         console.log("Updating connection status");
//         if (this._ismounted) {
//             this.setState({ status: this.getConnectionStatus() });
//         } else {
//             this._conn_status = this.getConnectionStatus();
//         }
//     }

//     handleMessage(msg: any) {
//         let obj = JSON.parse(msg);
//         console.debug(obj);
//         if (obj['type'] === null) {
//             console.error("Message has no 'type'");
//             return;
//         }

//         if (obj['type'] === 'YouJoined') {
//             console.debug("You have joined the game");
//             const gameState = obj['game_state'];
//             const player = new Player(obj['player']['username'], obj['player']['active']);
//             const owner = new Player(gameState['owner']['username'], gameState['owner']['active']);
//             const playersJson = gameState['players'];
//             const players: Map<string, Player> = new Map();
//             for (let pj of playersJson) {
//                 let newPlayer = new Player(pj['username'], pj['active']);
//                 players.set(newPlayer.username, newPlayer);
//             }
//             this.setState({
//                 player: player,
//                 owner: owner,
//                 players: players,
//                 game_state: parseState(gameState['state']),
//                 turn: gameState['turn'],
//                 order: gameState['order'],
//             });
//         } else if (obj['type'] === 'PlayerAdded') {
//             console.debug("Adding new player");
//             const new_player = new Player(obj['player']['username'], obj['player']['active']);
//             const map = this.state.players;
//             map.set(new_player.username, new_player);
//             this.setState({ players: map });
//         } else if (obj['type'] === 'PlayerDisconnected') {
//             const username = obj['player']['username'];
//             const map = this.state.players;
//             map.delete(username);
//             this.setState({ players: map });
//         } else if (obj['type'] === 'GameStarted') {
//             this.setState({ game_state: GameProgressState.Playing })
//         } else if (obj['type'] === 'NewOwner') {
//             console.info('Updating Owner');
//             const owner = new Player(obj['owner']['username'], obj['owner']['active'])
//             this.setState({ owner: owner });
//         } else {
//             console.warn(`Unidentifed message type '${obj['type']}'`);
//         }
//     }

//     createWebsocket(url: string) {
//         console.info("Creating websocket connection");
//         let websocket: WebSocket = new WebSocket(url);
//         // websocket.onopen = () => {this.updateConnectionState();}
//         websocket.onclose = () => this.updateConnectionState();
//         websocket.onerror = () => this.updateConnectionState();
//         websocket.onmessage = (ev) => this.handleMessage(ev.data);
//         return websocket;
//     }

//     joinGame() {
//         let msg: any = {
//             "type": "Activate",
//             "user_id": this.state.user_id,
//             "game_id": this.state.game_id,
//         }
//         this.state.websocket.send(JSON.stringify(msg));
//     }

//     render() {
//         let stateElement: JSX.Element = <span></span>;
//         if (this.state.game_state === GameProgressState.Lobby) {
//             stateElement = (
//                 <Lobby
//                     players={this.state.players}
//                     owner={this.state.owner}
//                     player={this.state.player}
//                     onClick={this.state.start_game_handler}
//                 />
//             );
//         } else if (this.state.game_state === GameProgressState.NoState) {
//             stateElement = <p>no state</p>;
//         } else if (this.state.game_state === GameProgressState.Playing) {
//             if (this.state.player !== undefined) {
//                 stateElement = (
//                     <GameScreen
//                         turn={this.state.turn}
//                         order={this.state.order}
//                         makeGuessCallback={this.state.makeGuessHandler}
//                         player={this.state.player}
//                     />
//                 )
//             }
//         } else if (this.state.game_state === GameProgressState.Finished) {
//             stateElement = <p>Finished</p>;
//         }

//         return (
//             <div>
//                 <p> Red or Black </p>
//                 <ConnStatus status={this.state.status} />
//                 {stateElement}
//             </div>
//         );
//     }

//     /* Callback */
//     startGameCallback() {
//         console.debug('Start game clicked');
//         let urlParams = this.state.url_params;
//         const msg = {
//             'type': 'StartGame',
//             'user_id': urlParams.user_id,
//             'game_id': urlParams.game_id,
//         };
//         this.state.websocket.send(JSON.stringify(msg));
//     }

//     makeGuessCallback(guess: Guess) {
//         if (this.state.player !== undefined && this.state.order.length > 0) {
//             const p = this.state.player;
//             let currentPlayer: Player = this.state.order[this.state.turn % this.state.order.length];
//             if (p.username === currentPlayer.username) {
//                 if (guess === Guess.Black) {
//                     console.debug('Black guess clicked');
//                 } else {
//                     console.debug('Red guess clicked');
//                 }
//             } else {
//                 console.log("It's not your turn")
//             }
//         }
//     }
// }


ReactDOM.render(<Game />, document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();

// export default Guess;