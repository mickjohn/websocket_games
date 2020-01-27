import React from 'react';
import './correct_box.css';

interface Props {
    show_box: boolean;
    clearCorrectCallback: () => void;
}


class CorrectBox extends React.Component<Props>   {
    render() {
        if (this.props.show_box) {
            return (
                <div className="CorrectBox">
                    Correct!!
                    <br />
                    <button onClick={(_e) => this.props.clearCorrectCallback()}>
                        Ok!
                    </button>
                </div>
            );
        }
        return null
    }
}

export default CorrectBox;