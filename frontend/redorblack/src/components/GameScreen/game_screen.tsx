import React from 'react';
import Player from '../../player';
import Guess from '../../utils/guess';
import './game_screen.css';
import aceOfDiamonds from './ace_diamonds.png';
import aceOfSpades from './ace_spades.png';
import { GameHistory } from '../../GameHistory'

interface Props {
    turn: number,
    order: Array<Player>,
    player: Player,
    game_history: GameHistory,
    makeGuessCallback: (guess: Guess) => void;
}

function getCurrentPlayer(players: Array<Player>, turn: number): Player | undefined {
    if (players.length === 0) {
        return undefined;
    }

    let index: number;
    index = turn % players.length;
    return players[index];
}

function getNextPlayer(players: Array<Player>, turn: number): Player | undefined {
    if (players.length === 0) {
        return undefined;
    }

    let index: number;
    index = (turn + 1) % players.length;
    return players[index];
}

class GameScreen extends React.Component<Props>   {

    guessButtonClicked(guess: Guess) {
        this.props.makeGuessCallback(guess);
    }

    constructor(props: Props) {
        super(props);
    }

    getPenaltyForThisPlayer(): number | null {
        const hist = this.props.game_history;
        if (hist.items().length === 0) {
            return null;
        }
        const item = hist.items()[0];
        if (item.username === this.props.player.username) {
            if (item.correct) {
                return item.penalty;
            }
        }
        return null;
    }

    createUpcomingPlayersBox(): JSX.Element {
        const nextPlayer = getNextPlayer(this.props.order, this.props.turn);
        const currentPlayer = getCurrentPlayer(this.props.order, this.props.turn);

        if (nextPlayer === undefined || currentPlayer === undefined) {
            return <span></span>;
        }

        if (nextPlayer === currentPlayer) {
            return <p><b>Next Player:</b> You're the only player!</p>;
        }

        if (currentPlayer.username === this.props.player.username) {
            return (
                <div>
                    <p><b>Current Player</b>: you!</p>
                    <p><b>Next Player</b> {nextPlayer.username}</p>
                </div>
            );
        }

        return (
            <div>
                <p><b>Current Player</b>: {currentPlayer.username}</p>
                <p><b>Next Player</b> {nextPlayer.username}</p>
            </div>
        )
    }

    // The guess sections shows the red/black buttons
    createGuessSection(): JSX.Element {
        return (
            <div>
                <h3>It's your turn!</h3>
                <div className="ButtonContainer">
                    <button onClick={(_e) => this.guessButtonClicked(Guess.Red)}>
                        <img src={aceOfDiamonds} width="120px" alt="guess red" />
                    </button>
                    <button onClick={(_e) => this.guessButtonClicked(Guess.Black)}>
                        <img src={aceOfSpades} width="120px" alt="guess black" />
                    </button>
                </div>
            </div>
        );
    }

    render() {
        let isTurn: boolean = false;
        const currentPlayer = getCurrentPlayer(this.props.order, this.props.turn);
        if (currentPlayer !== undefined && currentPlayer.username == this.props.player.username) {
            isTurn = true;
        }

        let choiceMenu: JSX.Element;
        if (isTurn) {
            choiceMenu = this.createGuessSection();
        } else {
            const username: string = currentPlayer !== undefined ? currentPlayer.username : '(unknown)';
            choiceMenu = (
                <div>
                    <p><span className="player-name">{username}</span> is guessing</p>
                    <div className="loader">
                        <div></div>
                        <div></div>
                        <div></div>
                    </div>
                </div>
            );
        }

        return (
            <div className="GameScreen">
                <div className="TopInfo">
                    {this.createUpcomingPlayersBox()}
                    <p>Cards Left: <b>N/A</b> </p>
                </div>
                {choiceMenu}
                <div>
                    <button>Game Overview</button>
                </div>
            </div>
        );
    }
}

export default GameScreen;