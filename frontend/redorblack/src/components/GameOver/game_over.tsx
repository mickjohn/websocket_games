import React from 'react';
import './game_over.css';
import trophy from './trophy.png';
import poop from './poop.png';
import woozy from './woozy.png';

interface Props {
    stats: Stats | null;
}

class Stat {
    usernames: string[];
    score: number;
    place: number;

    constructor(usernames: string[], score: number, place: number) {
        this.usernames = usernames;
        this.score = score;
        this.place = place;
    }
}

export class Stats {
    bestPlayers: Stat[];
    worstPlayers: Stat[];
    drunkestPlayers: Stat[];

    constructor(bestPlayers: Stat[], worstPlayes: Stat[], drunkestPlayers: Stat[]) {
        this.bestPlayers = bestPlayers;
        this.worstPlayers = worstPlayes;
        this.drunkestPlayers = drunkestPlayers;
    }
}

function getOrdinal(num_string: string): string {
    if (num_string.endsWith("11") || num_string.endsWith("12") || num_string.endsWith("13")) {
        return "th";
    } else  if (num_string.endsWith("1")) {
        return "st";
    } else if (num_string.endsWith("2")) {
        return "nd";
    } else if (num_string.endsWith("3")) {
        return "rd";
    } else {
        return "th";
    }

}

export function parseStats(stats: any): Stats {
    const statTypes: string[] = [
        "best_players",
        "worst_players",
        "drunkest_players",
    ];

    const parsedStats: Map<string, Stat[]> = new Map();

    for (const statType of statTypes) {
        parsedStats.set(statType, []);
        Object.keys(stats[statType]).forEach(function (key, index) {
            let item = stats[statType][key];
            let usernames = item[0];
            let score = item[1];
            let place = parseInt(key);
            let stat = new Stat(usernames, score, place);
            (parsedStats.get(statType) || []).push(stat);
        });
    }

    const bestPlayers: Stat[] = parsedStats.get('best_players') || [];
    const worstPlayers: Stat[] = parsedStats.get('worst_players') || [];
    const drunkestPlayers: Stat[] = parsedStats.get('drunkest_players') || [];

    return new Stats(bestPlayers, worstPlayers, drunkestPlayers);
}

class GameOver extends React.Component<Props>  {

    constructor(props: Props) {
        super(props);
    }

    renderScoreTable(title: JSX.Element, stats: Stat[], class_name: string, headers: [string, string, string]) {
        return (
            <div className={class_name}>
                <h2>{title}</h2>
                <table>
                    <tr>
                        <th>{ headers[0] }</th>
                        <th>{ headers[1] }</th>
                        <th>{ headers[2] }</th>
                    </tr>
                    {stats.map((item, index) => {
                        return (
                            <tr key={index}>
                                <td>{item.place}<sup>{getOrdinal(`${item.place}`)}</sup></td>
                                <td>{item.score}</td>
                                <td>{item.usernames.join('<br/>')}</td>
                            </tr>
                        )
                    })}
                </table>
            </div>
        )

    }

    render() {
        if (this.props.stats === null) {
            return null;
        }
        const stats: Stats = this.props.stats;
        const bestPlayersTitle = <h2>Best Players <img height="50" src={trophy} alt="trophy"></img></h2>;
        const worstPlayersTitle = <h2>Worst Players <img height="50" src={poop} alt="poop"></img></h2>;
        const drunkestPlayersTitle = <h2>Drunkest Players <img height="50" src={woozy} alt="woozy"></img></h2>;


        return (
            <div className="game-over">
                <h1>Game finished!</h1>
                {this.renderScoreTable(bestPlayersTitle, stats.bestPlayers, "best-players", ["Place", "Correct Guesses", "Players"])}
                {this.renderScoreTable(worstPlayersTitle, stats.worstPlayers, "worst-players", ["Place", "Wrong Guesses", "Players"])}
                {this.renderScoreTable(drunkestPlayersTitle, stats.drunkestPlayers, "drunkest-players", ["Place", "Seconds Drank", "Players"])}
            </div>
        )
    }
}

export default GameOver;