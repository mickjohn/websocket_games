import React from 'react';
import './history_box.css';
import { GameHistory, GameHistoryItem } from '../../GameHistory'

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
        let cardClass = guess == 'Red' ? 'red-guess' : 'black-guess';
        let playerGuess = guess == 'Red' ? 'red' : 'black';
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
        let listItems: Array<JSX.Element> = new Array();

        this.props.game_history.items().forEach(item => {
            listItems.push(<tr>
                {/* <td>{item.turn}</td> */}
                {this.createNameData(item.username)}
                {this.createGuessData(item.guess)}
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
                    <tr>
                        {/* <th>turn</th> */}
                        <th>username</th>
                        <th>guess</th>
                        <th>outcome</th>
                    </tr>
                    {listItems}
                </table>
            </div>
        );
    }
}

export default HistoryBox;