import React from 'react';
import Player from '../../player';
import Guess from '../../utils/guess';
import './game_screen.css';
import { GameHistory } from '../../GameHistory'
import DotsThrobber from '../DotsThrobber/dots_throbber';
import Card from '../../utils/card';

interface Props {
    turn: number,
    order: Player[],
    player: Player,
    gameHistory: GameHistory,
    currentCard: Card,
    makeGuessCallback: (guess: Guess) => void;
}


class GameScreen extends React.Component<Props>   {

    guessButtonClicked(guess: Guess) {
        this.props.makeGuessCallback(guess);
    }

    constructor(props: Props) {
        super(props);
    }

    getCurrentPlayer(): Player | undefined {
        if (this.props.order.length === 0) {
            return undefined;
        }

        const index: number = this.props.turn % this.props.order.length;
        return this.props.order[index];
    }

    createGuessSection(): JSX.Element {
        return (
            <div>
                <h3>It's your turn!</h3>
                <div className="ButtonContainer">
                    <button className="High" onClick={(_e) => this.guessButtonClicked(Guess.High)}>
                        High
                    </button>
                    {/* <button className="Same" onClick={(_e) => this.guessButtonClicked(Guess.High)}>
                        Same
                    </button> */}
                    <button className="Low" onClick={(_e) => this.guessButtonClicked(Guess.Low)}>
                        Low
                    </button>
                </div>
            </div>
        );
    }

    render() {
        let isTurn: boolean = false;
        const currentPlayer = this.getCurrentPlayer();
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
                    <DotsThrobber show={true} />
                </div>
            );
        }

        return (
            <div className="GameScreen">
                {choiceMenu}
            </div>
        );
    }
}

export default GameScreen;