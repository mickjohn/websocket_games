// type message: number;
import YouJoined from './you_joined';
import PlayerAdded from './player_added';
import PlayerDisconnected from './player_disconnected';
import GameStarted from './game_started';
import NewOwner from './new_owner';
import OrderChanged from './order_changed';
import GameFinished from './game_finished';
import GuessOutcome from './guess_outcome';
import ErrorMessage from './error_message';

export type Message = YouJoined
    | PlayerAdded
    | PlayerDisconnected
    | GameStarted
    | NewOwner
    | OrderChanged
    | GuessOutcome
    | GameFinished
    | Error;

export default function parseJsonMessage(msg: any): Message | null {
    const msgType = msg['type']
    let retval: Message | null = null;

    switch (msgType) {
        case YouJoined.msgtype: {
            console.debug("About to parse a YouJoined message");
            retval = YouJoined.fromJson(msg);
            break;
        }
        case PlayerAdded.msgtype: {
            console.debug("About to parse a PlayerAdded message");
            retval = PlayerAdded.fromJson(msg);
            break;
        }
        case PlayerDisconnected.msgtype: {
            console.debug("About to parse a PlayerDisconnected message");
            retval = PlayerDisconnected.fromJson(msg);
            break;
        }
        case GameStarted.msgtype: {
            console.debug("About to parse a GameStarted message");
            retval = GameStarted.fromJson(msg);
            break;
        }
        case GameFinished.msgtype: {
            console.debug("About to parse a GameOver message");
            retval = GameFinished.fromJson(msg);
            break;
        }
        case NewOwner.msgtype: {
            console.debug("About to parse a NewOwner message");
            retval = NewOwner.fromJson(msg);
            break;
        }
        case OrderChanged.msgtype: {
            console.debug("About to parse a OrderChanged message");
            retval = OrderChanged.fromJson(msg);
            break;
        }
        case GuessOutcome.msgtype: {
            console.debug("About to parse a GuessOutcome message");
            retval = GuessOutcome.fromJson(msg);
            break;
        }
        case ErrorMessage.msgtype: {
            console.debug("About to parse a ErrorMessage message");
            console.debug(`msg is ${JSON.stringify(msg)}`);
            retval = ErrorMessage.fromJson(msg);
            break;
        }
        default: {
            retval = null;
            break;
        }
    }
    return retval;
}

export {
    YouJoined,
    PlayerAdded,
    PlayerDisconnected,
    GameStarted,
    NewOwner,
    OrderChanged,
    GameFinished as GameOver,
    GuessOutcome,
    ErrorMessage,
}