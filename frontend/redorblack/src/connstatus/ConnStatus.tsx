import React from 'react';
import conn_error from './connection_error.svg';
import './ConnStatus.css';

export interface Props {
    status: number;
}

class ConnStatus extends React.Component<Props>   {

    render() {
        const status = this.props.status;
        let elem: JSX.Element;

        if (status !== WebSocket.OPEN && status !== WebSocket.CONNECTING) {
            elem = (
                <div className="ConnStatusError">
                    <h4>websocket connection error</h4>
                    <img src={conn_error} width="175px" alt="connection error" />
                </div>
            );
        } else {
            elem = (
                <h5>connected to server</h5>
            );
        }

        return (
            <div className="ConnStatus">
                {elem}
            </div>
        );
    }
}
export default ConnStatus;