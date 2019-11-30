import React from 'react';

interface Props {
    stats: any;
}

class Stat {
    usernames: string[];
    score: number;

    constructor(usernames: string[], score: number) {
        this.usernames = usernames;
        this.score = score;
    }
}

class Stats {
    bestPlayers: Stat;
    worstPlayers: Stat;
    drunkestPlayers: Stat;

    constructor(bestPlayers: Stat, worstPlayes: Stat, drunkestPlayers: Stat) {
        this.bestPlayers = bestPlayers;
        this.worstPlayers = worstPlayes;
        this.drunkestPlayers = drunkestPlayers;
    }
}

class GameOver extends React.Component<Props>  {

    constructor(props: Props) {
        super(props);
    }

    getBestPlayers() {

    }

    render() {
        return null
    }

}