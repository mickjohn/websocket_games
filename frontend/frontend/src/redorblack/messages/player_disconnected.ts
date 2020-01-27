import Player from '../../common/Player';

class PlayerDisconnected {
    static msgtype = "PlayerDisconnected";
    player: Player;

    constructor(player: Player) {
        this.player = player;
    }

    static fromJson(msg: any): PlayerDisconnected | null {
        const player = new Player(msg['player']['username'], msg['player']['active']);
        return new PlayerDisconnected(player);
    }
}

export default PlayerDisconnected;