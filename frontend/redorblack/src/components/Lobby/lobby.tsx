import React from 'react';
import Player from '../../player';
import './lobby.css';

interface Props {
    players: Map<string, Player>;
    owner: Player | undefined;
    player: Player | undefined;
    onClick: (event: any) => void;
}


class Lobby extends React.Component<Props>   {

    getPlayerList(players: Map<string, Player>) {
        const listItems: Array<JSX.Element> = [];
        this.props.players.forEach((value: Player, key: string) => {
            if (value.active) {
                listItems.push(<li key={value.username}>{key}</li>);
            }
        });
        return listItems;
    }

    getOwnerPart(owner: Player | undefined) {
        let ownerElem = <p>Waiting for owner to start...</p>;
        if (this.props.owner !== undefined && this.props.player !== undefined) {
            if (this.props.owner.username === this.props.player.username) {
                ownerElem = <button onClick={this.props.onClick}>Start</button>;
            } else {
                ownerElem = <p>Waiting for {this.props.owner.username} to start...</p>;
            }
        }
        return ownerElem
    }

    render() {
        const listItems: Array<JSX.Element> = this.getPlayerList(this.props.players);
        const ownerElem: JSX.Element = this.getOwnerPart(this.props.owner);

        return (
            <div className="Lobby">
                <h4>Start the game when all players have joined</h4>
                {ownerElem}
                <div className="PlayerList">
                    <h2>Players</h2>
                    <ul>{listItems}</ul >
                </div>
            </div >
        );
    }
}

export default Lobby;