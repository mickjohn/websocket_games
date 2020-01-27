import Player from '../../common/Player';
class NewOwner {
    static msgtype = "NewOwner";
    owner: Player;

    constructor(owner: Player) {
        this.owner = owner;
    }

    static fromJson(msg: any): NewOwner | null {
        return new NewOwner(new Player(msg['owner']['username'], msg['owner']['active']));
    }
}

export default NewOwner;