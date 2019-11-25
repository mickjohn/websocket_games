import React from 'react';
import './game_forms.css';

interface Props {
    submitHandler: (path: string, data: any) => void;
};

interface State {
    start_penalty: number;
    penalty_increment: number;
};

class RedOrBlack extends React.Component<Props, State> {

    constructor(props: any) {
        super(props);
        this.state = {
            start_penalty: 1,
            penalty_increment: 1,
        };

        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleChange(event: React.FormEvent<HTMLInputElement>): void {
        const value: string = event.currentTarget.value;
        const name: string = event.currentTarget.name;

        if (name === 'start_penalty') {
            this.setState({ start_penalty: parseInt(value) });
        } else if (name === 'penalty_increment') {
            this.setState({ penalty_increment: parseInt(value) });
        }
    }

    handleSubmit(e: React.FormEvent): void {
        e.preventDefault();
        const data = {
            'type': 'CreateGame',
            'options': {
                'penalty_start': this.state.start_penalty,
                'penalty_increment': this.state.penalty_increment,
            }
        };
        this.props.submitHandler('RedOrBlack', data);
    }

    render() {
        return (
            <div>
                <form className="GameSettings" onSubmit={this.handleSubmit}>
                    <h3>Settings for new Red Or Black game</h3>
                    <label htmlFor='start_penalty'><b>Starting Penalty</b></label>
                    <br />
                    <input id="start_penalty" name="start_penalty" type="number" min="1" value={this.state.start_penalty} onChange={this.handleChange} />
                    <br />

                    <label htmlFor="penalty_increment"><b>Penalty Increment</b></label>
                    <br />
                    <input id="penalty_increment" name="penalty_increment" type="number" min="1" value={this.state.penalty_increment} onChange={this.handleChange} />
                    <br />

                    <input type="submit" value="create" />
                </form>
            </div >
        );
    }
}

export default RedOrBlack;
