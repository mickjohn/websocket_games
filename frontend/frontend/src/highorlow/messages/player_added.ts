import Player from '../../common/Player';

class PlayerAdded {
    static msgtype = "PlayerAdded";
    player: Player;

    constructor(player: Player) {
        this.player = player;
    }

    static fromJson(msg: any): PlayerAdded | null {
        const player = new Player(msg['player']['username'], msg['player']['active']);
        return new PlayerAdded(player);
    }
}

export default PlayerAdded;