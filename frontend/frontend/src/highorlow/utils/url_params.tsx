export class UrlParams {
    user_id: string;
    game_id: string;

    constructor(user_id: string, game_id: string) {
        this.user_id = user_id;
        this.game_id = game_id;
    }
}

export default UrlParams;