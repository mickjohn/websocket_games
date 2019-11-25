class Config {
    websocketUrl: string;
    baseUrl: string;

    constructor(websocketUrl: string, baseUrl: string) {
        this.websocketUrl = websocketUrl;
        this.baseUrl = baseUrl;
    }
}

export const config: Config = new Config('wss://games.mickjohn.com:8010','games.mickjohn.com'); // CHANGEME #1

export default config;
