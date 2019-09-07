import React from 'react';
import Player from '../player';
import Guess from '../utils/guess';

interface Props {
    turn: number,
    order: Array<Player>,
    player: Player,
    makeGuessCallback: (guess: Guess) => void;
}


class GameScreen extends React.Component<Props>   {

    getNextPlayer(players: Array<Player>, turn: number) {
        if (players.length === 0) {
            return undefined;
        }

        let index: number;
        index = turn % players.length;
        return players[index];
    }

    // getCurrentPlayer(players: Array<Player>, turn: number) {
    //     if (players.length === 0) {
    //         return undefined;
    //     }

    //     let index: number;
    //     index = turn % players.length;
    //     return players[index];
    // }

    render() {
        let nextPlayerElem: JSX.Element;
        let isTurn: boolean = false;

        const nextPlayer = this.getNextPlayer(this.props.order, this.props.turn);
        if (nextPlayer !== undefined && nextPlayer.username === this.props.player.username) {
            nextPlayerElem = <p> It's yout turn!!! </p>
            isTurn = true;
        } else if (nextPlayer !== undefined) {
            nextPlayerElem = <p>Next Player: {nextPlayer.username} </p>
        } else {
            nextPlayerElem = <p>Next Player: - </p>
        }

        let choiceMenu: JSX.Element;
        if (isTurn) {
            choiceMenu = (
                <div>
                    <button onClick={(_e) => this.props.makeGuessCallback(Guess.Red)}>Red</button>
                    <button onClick={(_e) => this.props.makeGuessCallback(Guess.Black)}>Black</button>
                </div>
            );
        } else {
            choiceMenu = (
                <p> Not your turn </p>
            );
        }

        return (
            <div>
                <div>
                    {nextPlayerElem}
                    <p>Cards Left</p>
                </div>
                {choiceMenu}
                <div>
                    <p>Last Card: 5 hearts</p>
                    <button>Game Overview</button>
                </div>
            </div >
        );
    }
}

export default GameScreen;