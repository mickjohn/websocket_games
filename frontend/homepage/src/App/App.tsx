import React from 'react';
import * as resolver from '../resolver';
import './App.css';
import Game from '../Games';

import Spinner from '../Spinner/Spinner';
import ErrorBox from '../ErrorBox/ErrorBox';

// const websocketBaseUrl = 'ws://localhost:8080'
const websocketBaseUrl = 'ws://192.168.1.1:8080'

interface Props { };

interface State {
  username: string;
  gameCode: string;
  checking_msg: string;
  ws: WebSocket | null;
  error_msg: string;
  name_valid: boolean,
  code_entered: boolean,
}

class VerifyResult {
  ok: boolean;
  msg: string;
  game_type: Game | null;

  constructor(ok: boolean, msg: string, game_type: Game | null) {
    this.ok = ok;
    this.msg = msg;
    this.game_type = game_type;
  }
}

class App extends React.Component<Props, State> {

  constructor(props: any) {
    super(props);
    this.state = {
      username: '',
      gameCode: '',
      checking_msg: '',
      error_msg: '',
      ws: null,
      name_valid: false,
      code_entered: false,
    };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange(event: React.FormEvent<HTMLInputElement>): void {
    const value: string = event.currentTarget.value;
    const name: string = event.currentTarget.name;

    if (name === 'username') {
      this.setState({ name_valid: this.validateName(value) });
      this.setState({ username: value });
    } else {
      this.setState({ code_entered: this.validateCode(value) });
      this.setState({ gameCode: value });
    }
  }

  validateName(name: string): boolean {
    if (name.length > 10) {
      return false;
    }
    return true;
  }

  validateCode(code: string): boolean {
    if (code.length === 4) {
      return true;
    }
    return false;
  }

  verifyGameCode(code: string): VerifyResult {
    const num: number = resolver.DecodeGameCode(code);
    let return_val = new VerifyResult(false, '', null);
    if (num === null) {
      this.setState({ checking_msg: `Code is invalid` });
      return_val.ok = false;
      return_val.msg = 'Code is invalid';
      return return_val;
    }

    // Check code resolves to a game type
    const game: Game | null = resolver.lookupGame(num);
    if (game === null) {
      return_val.ok = false;
      return_val.msg = `${code} Code is invalid`;
      return return_val;
    }

    return_val.ok = true;
    return_val.game_type = game
    return return_val;
  }

  handleSubmit(event: any): void {
    event.preventDefault();
    const username = this.state.username;
    const code = this.state.gameCode.toUpperCase();
    // this.setState({ checking: true, checking_msg: 'Validating code...', error_msg: null });
    this.setState({ checking_msg: 'Validating code...', error_msg: '' });

    // Add a delay so that the UI looks like it's doing something :D
    setTimeout(() => {
      // Check code is ok
      const verify_result: VerifyResult = this.verifyGameCode(code);
      if (!verify_result.ok) {
        this.setState({ error_msg: verify_result.msg });
        this.reset();
        return;
      }

      this.setState({ checking_msg: `Connecting to ${verify_result.game_type} server...` });

      setTimeout(() => {
        // If so, create websocket
        if (verify_result.game_type !== null) {
          const websocketUrl = `${websocketBaseUrl}/${verify_result.game_type.path}`;
          const websocket: WebSocket = new WebSocket(websocketUrl);
          const game: Game = verify_result.game_type;
          this.setState({ ws: websocket });

          let wait_for_response_timeout: any;

          // When the websocket opens set a register message
          websocket.onopen = () => {
            const data = {
              'type': 'Register',
              'game_id': code,
              'username': username,
            }
            websocket.send(JSON.stringify(data));

            wait_for_response_timeout = setTimeout(() => {
              this.reset();
              this.setState({ error_msg: "timeout waiting for server response" });
            }, 5000);

          };

          // If the websocket is closed for some reason set an error msg and reset
          websocket.onclose = () => {
            console.log("WS connection closed");
            this.reset();
            this.setState({ error_msg: "cant connect to websocket server" });
          }

          // We only expect one message from the server. After we get it act
          // as appropriate.
          websocket.onmessage = (e) => {
            const msg = JSON.parse(e.data);
            console.debug(`msg from websocket = ${e.data}`);
            clearTimeout(wait_for_response_timeout);
            if (msg['type'] === 'Registered') {
              // We don't need this anymore
              // websocket.close();

              const user_id = msg['user_id'];
              console.debug(`user_id = ${user_id}`);

              this.setState({ checking_msg: `User added, redirecting to ${verify_result.game_type} page` });
              setTimeout(() => {
                console.debug('redirecting');
                window.location.href = `http:/localhost/${game.path}?game_id=${code}&uid=${user_id}`;
              }, 2000);

            } else if (msg['type'] === 'Error') {
              // Clear the onclose handler
              websocket.onclose = () => { };
              this.reset();
              this.setState({ error_msg: msg['error'] });
            }
          };
        } // End check game !== null if
      }, 1300); // End websocket timeout
    }, 1300); // End main timeout
  }

  reset(): void {
    if (this.state.ws !== null) {
      this.state.ws.close();
    }

    this.setState({
      checking_msg: '',
      ws: null,
    });
  }

  buildForm(): JSX.Element {
    let button: JSX.Element;
    if (this.state.name_valid && this.state.code_entered) {
      button = <input type="submit" value="Submit" />
    } else {
      button = <input disabled type="submit" value="Submit" />
    }

    return (
      <form onSubmit={this.handleSubmit}>
        <label className="App-label" htmlFor='username'><b>YOUR NAME</b></label>
        <br />
        <input id="username" name="username" minLength={4} maxLength={18} size={16} type="text" value={this.state.username} onChange={this.handleChange} />
        <br />

        <label className="App-label" htmlFor="gameCode"><b>GAME CODE</b></label>
        <br />
        <input id="gameCode" name="gameCode" minLength={4} maxLength={4} size={16} type="text" value={this.state.gameCode} onChange={this.handleChange} />
        <br />
        {button}
      </form>
    )
  }

  render() {
    let form: JSX.Element = this.buildForm();

    /* If the spinner is showing hide the form*/
    if (this.state.checking_msg) {
      form = <span></span>;
    } else {
      form = this.buildForm();
    }

    return (
      <div className="App" >
        <header className="App-header"> games.mickjohn.com </header>
        <ErrorBox message={this.state.error_msg}></ErrorBox>
        {form}
        <Spinner message={this.state.checking_msg}></Spinner>
      </div >
    );
  }
}

export default App;