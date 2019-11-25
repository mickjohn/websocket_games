import React from 'react';
import './game_info.css';
import Player from '../../player';
import vibrate from '../../utils/vibrate';

interface Props {
    turn: number,
    order: Array<Player>,
    player: Player | undefined,
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
            vibrate([100, 50, 100]);
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
        return this.createUpcomingPlayersBox();
    }
}

export default GameInfo;