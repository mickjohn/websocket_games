import React from 'react';
import './history_box.css';
import { GameHistory } from '../../../common/GameHistory'

interface Props {
    game_history: GameHistory,
}

class HistoryBox extends React.Component<Props>   {

    createNameData(username: string): JSX.Element {
        return (
            <td className="username">
                {username}
            </td>
        );
    }

    createGuessData(guess: string): JSX.Element {
        let cardClass = guess === 'Red' ? 'red-guess' : 'black-guess';
        let playerGuess = guess === 'Red' ? 'red' : 'black';
        return (
            <td>
                <span className={cardClass}>
                    {playerGuess}
                </span>
            </td>
        );
    }

    createOutcomeData(outcome: boolean): JSX.Element {
        let outcomeClass = outcome ? 'good-outcome' : 'bad-outcome';
        return (
            <td>
                <span className={outcomeClass}>{outcome ? 'Correct!' : 'Wrong!'}</span>
            </td>
        );
    }


    render() {
        let listItems: Array<JSX.Element> = [];

        this.props.game_history.items().forEach(item => {
            listItems.push(<tr>
                <td>{item.turn + 1}</td>
                {this.createNameData(item.player.username)}
                {this.createGuessData(item.guess)}
                <td>{item.card.rank.substring(0, 1)}{item.card.suitIcon}</td>
                {this.createOutcomeData(item.correct)}
            </tr>);
        });

        /* If there is no history, add a placeholder */
        if (listItems.length === 0) {
            listItems.push(
                <td>
                    game history...
                </td>
            );
        }

        return (
            <div className="HistoryBox">
                <table>
                    <tr className="HistoryBoxHeader" >
                        <th>turn</th>
                        <th>user</th>
                        <th>guess</th>
                        <th>card</th>
                        <th>outcome</th>
                    </tr>
                    {listItems}
                </table>
            </div>
        );
    }
}

export default HistoryBox;