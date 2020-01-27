import React from 'react';
import config from '../../../common/Config';
import Guess from '../../utils/guess';
import UrlParams from '../../utils/url_params';
import GameState from '../../utils/game_state';
import { GameHistory } from '../../GameHistory';
import vibrate from '../../../common/Vibrate';
import { Stats } from '../GameOver/game_over';
import parseJsonMessage from '../../messages/parser';
import * as messages from '../../messages/parser';

// Components:
import ConnStatus from '../../../common_components/ConnStatus/conn_status';
import Lobby from '../../../common_components/Lobby/lobby';
import GameScreen from '../GameScreen/game_screen';
import Player from '../../../common/Player';
import HistoryBox from '../HistoryBox/history_box';
import PenaltyBox from '../PenaltyBox/penalty_box';
import CorrectBox from '../CorrectBox/correct_box';
import DotsThrobber from '../../../common_components/DotsThrobber/dots_throbber';
import GameInfo from '../GameInfo/game_info';
import GameOver from '../GameOver/game_over';
import Modal from '../Modal/modal';
import PlayerList from '../../../common_components/PlayerList/player_list';

// Css:
import './game.css';
import '../Modal/modal.css';

function parseState(s: string): GameState {
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
    player?: Player;

    // The owner is the first player to join the game.
    // Only the owner can start the game
    owner?: Player;

    // The playing state of the game, e.g. lobby, finished
    game_state: GameState;

    // Game turn number
    turn: number;

    // The outcomes from the turns
    game_history: GameHistory;

    // The penalty to drink
    penalty: number | null;

    // The current penalty (for info)
    current_penalty?: number;

    // The number of cards left in the deck
    cards_left?: number;

    // If true show 'your correct box'
    show_correct: boolean;

    // Waiting for guess result
    waiting_for_result: boolean;

    // Array of players in order of thier turn
    order: Player[];

    // Stats
    stats: Stats | null;

    // Whether or not to show the modal
    show_modal: boolean;

    // What to do when start game clicked
    start_game_handler: (event: any) => void;

    // What to do when guess button is clicked
    makeGuessHandler: (guess: Guess) => void;

    // Function to clear the penalty.
    clearPenaltyHandler: () => void;

    // Function to cleat the correct box.
    clearCorrectCallback: () => void;

    // Function to close the modal
    closeModalCallback: () => void;
}

interface Props { }

class Game extends React.Component<Props, State>   {
    // _ismounted: boolean;
    _conn_status: string;

    constructor(props: Props) {
        super(props);

        if (!this.hasUrlParams()) {
            this.redirect();
        }

        let params: UrlParams = this.getUrlParams();

        // this._ismounted = false;
        this._conn_status = "not connected";
        let websocket: WebSocket = this.createWebsocket(`${config.websocketUrl}/game_${params.game_id}`);
        this.state = {
            websocketStatus: WebSocket.CLOSED,
            websocket: websocket,
            user_id: params.user_id,
            game_id: params.game_id,
            players: new Map(),
            game_history: new GameHistory(),
            player: undefined,
            show_correct: false,
            owner: undefined,
            game_state: GameState.NoState,
            start_game_handler: this.startGameCallback.bind(this),
            makeGuessHandler: this.makeGuessCallback.bind(this),
            clearPenaltyHandler: this.clearPenaltyHandler.bind(this),
            clearCorrectCallback: this.clearCorrectCallback.bind(this),
            closeModalCallback: this.closeModalCallback.bind(this),
            turn: 0,
            penalty: null,
            current_penalty: undefined,
            waiting_for_result: false,
            order: [],
            cards_left: undefined,
            stats: null,
            show_modal: false,
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
        window.location.href = url;
    }

    getCurrentPlayer(): Player | undefined {
        if (this.state.order.length > 0) {
            const index: number = this.state.turn % this.state.order.length;
            const currentPlayer: Player = this.state.order[index];
            return currentPlayer;
        }
        return undefined;
    }

    getNextPlayer(): Player | null {
        if (this.state.order.length > 0) {
            const nextIndex: number = this.state.turn + 1 % this.state.order.length;
            const nextPlayer: Player = this.state.order[nextIndex];
            return nextPlayer
        }
        return null;
    }

    isPlayersGo(): boolean {
        const currentPlayer = this.getCurrentPlayer();
        if (currentPlayer !== undefined) {
            return this.state.player !== undefined && this.state.player.username === currentPlayer.username;
        }
        return false;
    }

    goingNext(): boolean {
        const nextPlayer: Player | null = this.getNextPlayer();
        if (nextPlayer !== null) {
            return this.state.player !== undefined && this.state.player === nextPlayer;
        }
        return false;
    }

    handleMessage(msg: any): void {
        let obj = JSON.parse(msg);
        console.debug(obj);
        if (obj['type'] === null) {
            console.error("Message has no 'type'");
            return;
        }

        let parsed_message: messages.Message | null = parseJsonMessage(obj);
        if (parsed_message === null) {
            return;
        }

        if (parsed_message instanceof messages.YouJoined) {
            /*************/
            /* YouJoined */
            /*************/
            this.setState({
                player: parsed_message.player,
                owner: parsed_message.owner,
                players: parsed_message.players,
                game_state: parsed_message.state,
                turn: parsed_message.turn,
                order: parsed_message.order,
                game_history: parsed_message.history,
                stats: parsed_message.stats,
                cards_left: parsed_message.cardsLeft,
                current_penalty: parsed_message.penalty,
            });
        } else if (parsed_message instanceof messages.PlayerAdded) {
            /***************/
            /* PlayerAdded */
            /***************/
            const map = this.state.players;
            map.set(parsed_message.player.username, parsed_message.player);
            this.setState({ players: map });
        } else if (parsed_message instanceof messages.PlayerDisconnected) {
            /**********************/
            /* PlayerDisconnected */
            /**********************/
            const map = this.state.players;
            map.delete(parsed_message.player.username);
            this.setState({ players: map });
        } else if (parsed_message instanceof messages.GameStarted) {
            /***************/
            /* GameStarted */
            /***************/
            this.setState({ game_state: GameState.Playing })
        } else if (parsed_message instanceof messages.NewOwner) {
            /************/
            /* NewOwner */
            /************/
            this.setState({ owner: parsed_message.owner });
        } else if (parsed_message instanceof messages.OrderChanged) {
            /****************/
            /* OrderChanged */
            /****************/
            this.setState({ order: parsed_message.order });
            // } else if (obj['type'] === 'GuessOutcome') {
        } else if (parsed_message instanceof messages.GuessOutcome) {
            /****************/
            /* GuessOutcome */
            /****************/
            const show_correct: boolean = this.isPlayersGo() && parsed_message.correct;

            // If this player is up next, vibrate.
            if (this.goingNext()) {
                vibrate([50, 50, 50]);
            }

            const items = this.state.game_history;
            items.addItem(parsed_message.createGameHistoryItem());

            // Update the turn number and history
            // Don't accidently clear the penalty
            let penalty: number | null = this.state.penalty;
            if (this.state.penalty === null) {
                penalty = this.getPenaltyForThisPlayer();
            }

            // The 'turn' number in the message is the turn just played, so add
            // 1 to it to get the current turn.
            const currentTurn = parsed_message.turn + 1;
            this.setState({
                turn: currentTurn,
                game_history: items,
                penalty: penalty,
                current_penalty: parsed_message.newPenalty,
                show_correct: show_correct,
                waiting_for_result: false,
                cards_left: parsed_message.cardsLeft,
            });
        } else if (parsed_message instanceof messages.GameOver) {
            /************/
            /* GameOver */
            /************/
            this.setState({ stats: parsed_message.stats, game_state: GameState.Finished });
        } else if (parsed_message instanceof messages.ErrorMessage) {
            /**********/
            /* Errors */
            /**********/
            if (parsed_message.errorType === 'GameNotFound') {
                this.redirect();
            }
        } else {
            console.warn(`Unidentifed message type '${obj['type']}'`);
        }
    }


    createWebsocket(url: string): WebSocket {
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
        if (item.player.username === this.state.player.username) {
            if (!item.correct) {
                return item.penalty;
            }
        }
        return null;
    }

    render() {
        let isPlaying = this.state.game_state === GameState.Playing;
        let isFinished = this.state.game_state === GameState.Finished;
        let stateElement: JSX.Element | null = null;

        const classes: string[] = [];
        if (this.state.show_modal) {
            classes.push("modal");
        }

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

        let lobby: JSX.Element | null = null;
        if (this.state.game_state === GameState.Lobby && this.websocketIsConnected()) {
            lobby = (
                <Lobby
                    players={this.state.players}
                    owner={this.state.owner}
                    player={this.state.player}
                    onClick={this.state.start_game_handler}
                />
            );
        }

        let gameInfo: JSX.Element | null = null;
        if (this.state.game_state === GameState.Playing) {
            gameInfo = <GameInfo
                turn={this.state.turn}
                order={this.state.order}
                player={this.state.player}
                cards_left={this.state.cards_left}
                penalty={this.state.current_penalty}
            />
        }

        return (
            <div className={classes.join(" ")}>
                <header className="GameHeader">Red or Black</header>
                <div className="GameScreen">
                    <ConnStatus status={this.state.websocketStatus} />
                    <h3>game id is {this.state.game_id}</h3>
                    {isPlaying &&
                        <>
                            {gameInfo}

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

                            <button
                                className="ShowHistoryButton"
                                onClick={() => this.setState({ show_modal: true })}
                            >
                                Show History
                            </button>

                            {this.state.show_modal &&
                                <Modal className="HistoryModal" closeModal={this.state.closeModalCallback}>
                                    <button onClick={() => this.setState({ show_modal: false })} >Close</button>
                                    {this.isPlayersGo() && <h3>It's your Go!</h3>}
                                    <HistoryBox game_history={this.state.game_history} />
                                </Modal>
                            }

                            <PlayerList order={this.state.order} currentPlayer={this.getCurrentPlayer()} />
                        </>
                    }

                    {/* Show the game over screen and stats if game is finished */}
                    {isFinished && <GameOver stats={this.state.stats} />}

                    {/* Show lobby if not playing  */}
                    {this.state.game_state === GameState.Lobby && lobby}
                </div>
            </div>
        );
    }

    /*************/
    /* Callbacks */
    /*************/
    startGameCallback() {
        let userId: string = this.state.user_id;
        const msg = {
            'type': 'StartGame',
            'user_id': userId,
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
        vibrate(40);
        this.setState({ penalty: null });
    }

    clearCorrectCallback() {
        vibrate(40);
        this.setState({ show_correct: false });
    }

    closeModalCallback() {
        this.setState({ show_modal: false });
    }

    /*****************/
    /* End Callbacks */
    /*****************/
}



export default Game;
export { parseState };