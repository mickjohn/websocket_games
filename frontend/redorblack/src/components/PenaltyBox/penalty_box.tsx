import React from 'react';
import './penalty_box.css';

interface Props {
    penalty: number;
}


class PenaltyBox extends React.Component<Props>   {

    constructor(props: Props) {
        super(props);
    }

    render() {
        return (
            <div className="penalty-box">
                Wrong! drink for {this.props.penalty}
            </div>
        );
    }
}

export default PenaltyBox;