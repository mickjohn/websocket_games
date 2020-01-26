import React from 'react';
import './ErrorBox.css';

interface Props {
    message: string;
};

class Error extends React.Component<Props> {
    render() {
        let error: JSX.Element;
        if (this.props.message) {
            error = (
                <div className="ErrorBox">
                    <h3> Something went wrong</h3>
                    <p>{this.props.message}</p>
                </div>
            );
        } else {
            error = <span></span>;
        }

        return error;
    }
}

export default Error;