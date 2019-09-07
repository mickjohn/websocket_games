import React from 'react';
import conn_error from './connection_error.svg';
import './ConnStatus.css';
import { stat } from 'fs';

export interface Props {
    status: number;
}

class ConnStatus extends React.Component<Props>   {

    getConnectionStatusString(): string {
        let status = this.props.status;
        if (status === WebSocket.OPEN) {
            return "connected";
        } else if (status === WebSocket.CLOSED) {
            return "not connected";
        } else if (status === WebSocket.CONNECTING) {
            return "connecting";
        } else if (status === WebSocket.CLOSING) {
            return "closing";
        }
        return "not connected";

    }


    render() {
        const status = this.props.status;
        
        if(status !== WebSocket.OPEN || status !== WebSocket.CONNECTING) {

        }

        return (
            <div className="ConnStatus">
                <img src={conn_error} width="175px" alt="connection error" />
                <p>
                    Websocket connection = {this.getConnectionStatusString()}
                </p>
            </div>
        );
    }
}
export default ConnStatus;