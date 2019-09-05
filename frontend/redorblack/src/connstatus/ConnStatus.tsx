import React from 'react';

export interface Props {
    status: string;
}

class ConnStatus extends React.Component<Props>   {
    render() {
        return (
            <div className="ConnStatus">
                <p>
                    Websocket connection = {this.props.status}
                </p>
            </div>
        );
    }
}
export default ConnStatus;