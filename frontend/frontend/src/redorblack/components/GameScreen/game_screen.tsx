import React from 'react';
import Player from '../../../common/Player';
import Guess from '../../utils/guess';
import './game_screen.css';
import { GameHistory } from '../../../common/GameHistory'
import DotsThrobber from '../../../common_components/DotsThrobber/dots_throbber';


interface Props {
    turn: number,
    order: Player[],
    player: Player,
    game_history: GameHistory,
    makeGuessCallback: (guess: Guess) => void;
}


class GameScreen extends React.Component<Props>   {

    guessButtonClicked(guess: Guess) {
        this.props.makeGuessCallback(guess);
    }

    getCurrentPlayer(): Player | undefined {
        if (this.props.order.length === 0) {
            return undefined;
        }

        const index: number = this.props.turn % this.props.order.length;
        return this.props.order[index];
    }

    // The guess sections shows the red/black buttons
    createGuessSection(): JSX.Element {
        return (
            <div>
                <h3>It's your turn!</h3>
                <div className="ButtonContainer">
                    <button className="Red" onClick={(_e) => this.guessButtonClicked(Guess.Red)}>
                        Red
                    </button>
                    <button className="Black" onClick={(_e) => this.guessButtonClicked(Guess.Black)}>
                        Black
                    </button>
                </div>
            </div>
        );
    }

    render() {
        let isTurn: boolean = false;
        const currentPlayer = this.getCurrentPlayer();
        if (currentPlayer !== undefined && currentPlayer.username === this.props.player.username) {
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