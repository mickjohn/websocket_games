class Config {
    websocketUrl: string;
    baseUrl: string;

    constructor(websocketUrl: string, baseUrl: string) {
        this.websocketUrl = websocketUrl;
        this.baseUrl = baseUrl;
    }
}

export const config: Config = new Config('ws://prod:9000','prod:9080'); // CHANGEME #1

export default config;
