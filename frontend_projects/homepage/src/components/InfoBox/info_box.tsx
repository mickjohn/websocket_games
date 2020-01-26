import React from 'react';
import './info_box.css';
import infoPng from './info.png';

interface Props {
    message: string | null;
}

class InfoBox extends React.Component<Props> {
    constructor(props: any) {
        super(props);

    }

    render() {
        return (
            <div className="infobox">
                {/* <span className="infobox-exclamation">!</span> */}
                <img src={infoPng} height="42" width="42"></img>
                <span className="infobox-message">{this.props.message}</span>
            </div>
        );
    }
}

export default InfoBox;