import React from 'react';
import Player from '../player';
import Guess from '../utils/guess';
import './GameScreen.css';
import aceOfDiamonds from './ace_diamonds.png';
import aceOfSpades from './ace_spades.png';

interface Props {
    turn: number,
    order: Array<Player>,
    player: Player,
    makeGuessCallback: (guess: Guess) => void;
}


class GameScreen extends React.Component<Props>   {

    getCurrentPlayer(players: Array<Player>, turn: number): Player | undefined {
        if (players.length === 0) {
            return undefined;
        }

        let index: number;
        index = turn % players.length;
        return players[index];
    }

    getNextPlayer(players: Array<Player>, turn: number): Player | undefined {
        if (players.length === 0) {
            return undefined;
        }

        let index: number;
        index = (turn + 1) % players.length;
        return players[index];
    }

    createUpcomingPlayersBox(): JSX.Element {
        const nextPlayer = this.getNextPlayer(this.props.order, this.props.turn);
        const currentPlayer = this.getCurrentPlayer(this.props.order, this.props.turn);

        if (nextPlayer === undefined || currentPlayer === undefined) {
            return <span></span>;
        }

        if (nextPlayer === currentPlayer) {
            return (
                <p><b>Next Player:</b> You're the only player!</p>
            );
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

    render() {
        let isTurn: boolean = false;
        const currentPlayer = this.getCurrentPlayer(this.props.order, this.props.turn);
        if (currentPlayer !== undefined && currentPlayer.username == this.props.player.username) {
            isTurn = true;
        } 

        let choiceMenu: JSX.Element;
        if (isTurn) {
            choiceMenu = (
                <div>
                    <h3>It's your turn!</h3>
                    <div className="ButtonContainer">
                        <button onClick={(_e) => this.props.makeGuessCallback(Guess.Red)}>
                            <p>Red</p>
                            <img src={aceOfDiamonds} width="150px" alt="guess red" />
                        </button>
                        <button onClick={(_e) => this.props.makeGuessCallback(Guess.Black)}>
                            <img src={aceOfSpades} width="150px" alt="guess black" />
                        </button>
                    </div>
                </div>
            );
        } else {
            choiceMenu = (
                <div className="ButtonContainer">
                    <p> Not your turn </p>
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
                    <p>Last Card: 5 hearts</p>
                    <button>Game Overview</button>
                </div>
            </div>
        );
    }
}

export default GameScreen;