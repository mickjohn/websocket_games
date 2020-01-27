import React from 'react';
import './dots_throbber.css';

interface Props {
    show?: boolean;
}

export function DotsThrobber(props: Props) {
    if (props.show) {
        return (
            <div className="loader">
                <div></div>
                <div></div>
                <div></div>
            </div>
        );
    }
    return null;
}

export default DotsThrobber