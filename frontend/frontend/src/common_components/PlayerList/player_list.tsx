import React from 'react';
import './player_list.css';
import Player from '../../common/Player';


interface Props {
    order: Player[];
    currentPlayer?: Player;
}


class PlayerList extends React.Component<Props>   {

    render() {
        const listItems: JSX.Element[] = [];
        for (let player of this.props.order) {
            if (this.props.currentPlayer !== undefined) {
                if (this.props.currentPlayer.username === player.username) {
                    listItems.push(<li className="PlayerListCurrentPlayer">{player.username}</li>);
                } else {
                    listItems.push(<li>{player.username}</li>);
                }
            }

        }

        return (
            <div className="PlayerList">
                <h1><u>Players</u></h1>
                <ul>
                    {listItems}
                </ul>
            </div>
        );
    }
}

export default PlayerList;