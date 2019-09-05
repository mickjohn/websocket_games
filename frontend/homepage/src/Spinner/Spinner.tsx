import React from 'react';
import './Spinner.css';

interface Props {
    message: string;
};


class Spinner extends React.Component<Props> {
    render() {
        let spinner: JSX.Element;
        if (this.props.message) {
            spinner = (
                <div>
                    <h1>Checking...</h1>
                    <div className="Spinner"></div>
                    <p className="Spinner-message">{this.props.message}</p>
                </div>
            );
        } else {
            spinner = <span></span>;
        }

        return spinner;
    }
}

export default Spinner;