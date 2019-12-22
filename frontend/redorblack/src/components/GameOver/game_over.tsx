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

    bestPlayers: Stat[];

    constructor(props: Props) {
        super(props);
        this.bestPlayers = [];
        for (const stat_json of props.stats['best_players']) {
            console.log(`stat_json = ${stat_json}`);
            const score = stat_json[0];
            const usernames = stat_json[1];
            const newStat = new Stat(usernames, score);
            this.bestPlayers.push(newStat);
        }
        console.log(`bestplayers = ${this.bestPlayers}`);
    }

    getBestPlayers() {

    }

    render() {
        return (
            <div>
                <div>
                    <h3>Best Players</h3>
                    <table>
                        <tr>
                            <th>Score</th>
                            <th>Players</th>
                        </tr>
                        {this.bestPlayers.map((item, index) => {
                            return (
                                <tr key={index}>
                                    <td>{item.score}</td>
                                    <td>{item.usernames}</td>
                                </tr>
                            )
                        })}
                    </table>
                </div>
            </div >
        )
    }
}

export default GameOver;