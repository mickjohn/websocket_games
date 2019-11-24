class Config {
    websocketUrl: string;
    baseUrl: string;

    constructor(websocketUrl: string, baseUrl: string) {
        this.websocketUrl = websocketUrl;
        this.baseUrl = baseUrl;
    }
}

export const config: Config = new Config('games.mickjohn.com:9000','localhost');
// export const config: Config = new Config('localhost:8080','localhost');

export default config;
