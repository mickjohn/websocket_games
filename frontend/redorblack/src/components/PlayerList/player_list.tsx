import React from 'react';
import './player_list.css';
import Player from '../../player';

interface Props {
    order: Player[];
    currentPlayer?: Player;
}


class PlayerList extends React.Component<Props>   {

    constructor(props: Props) {
        super(props);
    }

    render() {
        const listItems: JSX.Element[] = [];
        for (let player of this.props.order) {
            if (this.props.currentPlayer !== undefined) {
                if (this.props.currentPlayer.username == player.username) {
                    listItems.push(<li className="PlayerListCurrentPlayer">{player.username}</li>);
                } else {
                    listItems.push(<li>{player.username}</li>);
                }
            }

        }

        return (
            <>
                <h3>Players</h3>
                <ul className="PlayerList">
                    {listItems}
                </ul>
            </>
        );
    }
}

export default PlayerList;