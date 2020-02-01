import React from 'react';
import RedOrBlack from '../GameForms/red_or_black';
import HighOrLow from '../GameForms/high_or_low';
import { games } from '../../Games';

interface Props {
    createNewGameHandler: (path: string, data: any) => void;
    closeHandler: () => void;
}

interface State {
    selected_game: string;
}

export class CreateGame extends React.Component<Props, State> {

    constructor(props: Props, state: State) {
        super(props);
        this.gameSelectionChanged = this.gameSelectionChanged.bind(this);
        this.state = {
            selected_game: games[0].path,
        };
    }

    render() {
        const options = games.map((game) =>
            <option value={game.path}>{game.displayName}</option>
        );

        let formElement: JSX.Element | null = null;
        switch (this.state.selected_game) {
            case "redorblack":
                formElement = <RedOrBlack submitHandler={this.props.createNewGameHandler} />;
                break;
            case "highorlow":
                formElement = <HighOrLow submitHandler={this.props.createNewGameHandler} />;
                break;
            default:
                break;
        }

        return (
            <div>
                <select onInput={this.gameSelectionChanged} name="game">
                    {options}
                </select>

                {formElement}

                <button
                    className="CancelButton"
                    onClick={() => this.props.closeHandler()}
                >
                    cancel
                </button>
            </div>
        )
    }

    gameSelectionChanged(e: React.FormEvent<HTMLSelectElement>) {
        let newValue: string = e.currentTarget.value;
        this.setState({ selected_game: newValue });
    }

}

export default CreateGame;