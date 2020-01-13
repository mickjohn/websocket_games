import React from 'react';
import './game_info.css';
import Player from '../../player';
import Card from '../../utils/card';

// SVGs
import Clubs from './clubs.svg';
import Spades from './spades.svg';
import Hearts from './hearts.svg';
import Diamonds from './diamonds.svg';

interface Props {
    turn: number,
    order: Array<Player>,
    player: Player | undefined,
    cards_left: number | null;
    penalty: number | null;
    currentCard: Card;
}


class GameInfo extends React.Component<Props>   {

    constructor(props: Props) {
        super(props);
    }

    getCurrentPlayer(): Player | undefined {
        if (this.props.order.length === 0) {
            return undefined;
        }

        let index: number;
        index = this.props.turn % this.props.order.length;
        return this.props.order[index];
    }

    getNextPlayer(): Player | undefined {
        if (this.props.order.length === 0) {
            return undefined;
        }

        let index: number;
        index = (this.props.turn + 1) % this.props.order.length;
        return this.props.order[index];
    }

    createUpcomingPlayersBox(): JSX.Element | null {
        const nextPlayer = this.getNextPlayer();
        const currentPlayer = this.getCurrentPlayer();

        if (nextPlayer === undefined || currentPlayer === undefined) {
            return null;
        }

        if (nextPlayer === currentPlayer) {
            return <p><b>Next Player:</b> You're the only player!</p>;
        }

        if (this.props.player !== undefined && currentPlayer.username === this.props.player.username) {
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

    getSuitSvg(): string {
        const suit = this.props.currentCard.suit;
        if (suit == 'Clubs') {
            return Clubs;
        } else if (suit == 'Spades') {
            return Spades;
        } else if (suit == 'Hearts') {
            return Hearts;
        } else {
            return Diamonds;
        }
    }

    render() {
        let penaltyElem = null;
        if (this.props.penalty !== null) {
            penaltyElem = <span><b>Current Penalty:</b> {this.props.penalty}s </span>
        }

        let cardsLeft = null;
        if (this.props.cards_left !== null) {
            cardsLeft = <span><b>Cards Left:</b> {this.props.cards_left} </span>
        }

        return (
            <div>
                {this.createUpcomingPlayersBox()}
                {penaltyElem}
                {cardsLeft}
                <br />
                <div className="TopInfoCurrentCard">
                    Current Card
                    <br />
                    <span className="CardRank">{this.props.currentCard.rank}</span>
                    <img src={this.getSuitSvg()} alt={this.props.currentCard.suit} height="30" width="30"></img>
                </div>
            </div>
        )
    }
}

export default GameInfo;
