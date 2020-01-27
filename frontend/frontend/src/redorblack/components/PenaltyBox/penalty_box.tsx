import React from 'react';
import './penalty_box.css';

interface Props {
    penalty: number | null;
    clearPenaltyCallback: () => void;
}


class PenaltyBox extends React.Component<Props>   {

    render() {
        if (this.props.penalty !== null) {
            return (
                <div className="PenaltyBox">
                    Wrong! drink for {this.props.penalty}s
                    <br />
                    <button onClick={(_e) => this.props.clearPenaltyCallback()}>
                        Ok!
                    </button>
                </div>
            );
        }
        return null
    }
}

export default PenaltyBox;