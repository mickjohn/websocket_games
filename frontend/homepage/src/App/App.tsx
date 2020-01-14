import React from 'react';
import * as resolver from '../resolver';
import './App.css';
import Game, { games } from '../Games';

import Spinner from '../components/Spinner/Spinner';
import ErrorBox from '../components/ErrorBox/ErrorBox';
import RedOrBlack from '../components/GameForms/red_or_black';
import HighOrLow from '../components/GameForms/high_or_low';
import InfoBox from '../components/InfoBox/info_box';

// const websocketBaseUrl = 'ws://localhost:8080'
const websocketBaseUrl = 'wss://games.mickjohn.com:8010' // CHANGEME #2

interface Props { };

interface State {
  username: string;
  gameCode: string;
  checking_msg: string;
  ws: WebSocket | null;
  error_msg: string;
  name_valid: boolean,
  code_entered: boolean,
  show_create_game: boolean;
  selected_game: string;
  creating_game_message: string | null;
  info_box_message: string | null;
  game_created: boolean;
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
      show_create_game: false,
      selected_game: games[0].path,
      creating_game_message: null,
      info_box_message: null,
      game_created: false,
    };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.createNewGame = this.createNewGame.bind(this);
    this.gameSelectionChanged = this.gameSelectionChanged.bind(this);
  }

  handleChange(event: React.FormEvent<HTMLInputElement>): void {
    const value: string = event.currentTarget.value;
    const name: string = event.currentTarget.name;

    if (name === 'username') {
      this.setState({ name_valid: this.validateName(value), username: value });
    } else {
      this.setState({ code_entered: this.validateCode(value), gameCode: value });
    }
  }

  validateName(name: string): boolean {
    return name.length <= 10;
  }

  validateCode(code: string): boolean {
    return code.length === 4;
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
          const websocketUrl = `${websocketBaseUrl}/game_${code}`;
          console.info("websocket URL = " + websocketUrl);
          const websocket: WebSocket = new WebSocket(websocketUrl);
          const game: Game = verify_result.game_type;
          this.setState({ ws: websocket });

          let wait_for_response_timeout: any;

          // When the websocket opens set a register message
          websocket.onopen = () => {
            const data = {
              'type': 'Register',
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
              const user_id = msg['user_id'];
              console.debug(`user_id = ${user_id}`);

              this.setState({ checking_msg: `User added, redirecting to ${verify_result.game_type} page` });
              setTimeout(() => {
                const redirectUrl = `/${game.path}?game_id=${code}&uid=${user_id}`;
                console.debug(`redirecting to ${redirectUrl}`);
                window.location.href = redirectUrl;
              }, 800);

            } else if (msg['type'] === 'Error') {
              // Clear the onclose handler
              websocket.onclose = () => { };
              this.reset();
              this.setState({ error_msg: msg['error'] });
            }
          };
        } // End check game !== null if
      }, 800); // End websocket timeout
    }, 800); // End main timeout
  }

  /* Connect to Websocket server and create a new game */
  createNewGame(path: string, data: any) {
    const websocketUrl = `${websocketBaseUrl}/${path}`;
    console.info("websocket URL = " + websocketUrl);
    const websocket: WebSocket = new WebSocket(websocketUrl);
    this.setState({ creating_game_message: `Creating game...` });

    // When the websocket opens send the create game message
    websocket.onopen = () => {
      websocket.send(JSON.stringify(data));
    };

    const wait_for_response_timeout = setTimeout(() => {
      this.reset();
      this.setState({ error_msg: "timeout waiting for server response" });
    }, 5000);

    // If the websocket is closed for some reason set an error msg and reset
    websocket.onclose = () => {
      console.log("WS connection closed");
      this.reset();
      this.setState({ error_msg: "cant connect to websocket server" });
    }

    websocket.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      console.debug(`msg from websocket = ${e.data}`);
      clearTimeout(wait_for_response_timeout);
      if (msg['type'] === 'GameCreated') {
        const game_code = msg['game_code'];
        this.setState({
          gameCode: game_code,
          info_box_message: `Game created! Code is ${game_code}`,
          show_create_game: false,
          code_entered: true,
          game_created: true,
        });
      } else if (msg['type'] === 'Error') {
        // Clear the onclose handler
        websocket.onclose = () => { };
        this.reset();
        this.setState({ error_msg: msg['error'] });
      }
    };

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
        <input id="username" name="username" autoComplete="off" minLength={4} maxLength={18} size={16} type="text" value={this.state.username} onChange={this.handleChange} />
        <br />

        <label className="App-label" htmlFor="gameCode"><b>GAME CODE</b></label>
        <br />
        <input id="gameCode" name="gameCode" autoComplete="off" minLength={4} maxLength={4} size={16} type="text" value={this.state.gameCode} onChange={this.handleChange} />
        <br />
        {button}
      </form>
    )
  }

  gameSelectionChanged(e: React.FormEvent<HTMLSelectElement>) {
    let newValue: string = e.currentTarget.value;
    console.log(`Target value = ${newValue}`);
    this.setState({ selected_game: newValue });
  }

  createGameWindow() {
    const options = games.map((game) =>
      <option value={game.path}>{game.displayName}</option>
    );

    let formElement: JSX.Element | null = null;
    switch (this.state.selected_game) {
      case "redorblack":
        formElement = <RedOrBlack submitHandler={this.createNewGame} />;
        break;
      case "highorlow":
        formElement = <HighOrLow submitHandler={this.createNewGame} />;
        break;
      default:
        break;
    }

    return (
      <div>
        <select onInput={this.gameSelectionChanged} name="game">
          {options}
        </select>

        {formElement}

        <button
          className="CancelButton"
          onClick={() => this.setState({ show_create_game: false })}
        >
          cancel
        </button>

        <h3>{this.state.creating_game_message}</h3>
      </div>
    )
  }

  createJoinDiv() {
    const form: JSX.Element | null = this.state.checking_msg ? null : this.buildForm();
    const game_created = this.state.game_created;

    return (
      <div>
        <ErrorBox message={this.state.error_msg}></ErrorBox>
        {form}
        <Spinner message={this.state.checking_msg}></Spinner>

        {!game_created && <h3>────────── OR ──────────</h3>}

        {!game_created && <button
          className="CreateGameButton"
          onClick={() => this.setState({ show_create_game: true })}
        >
          Create a game
        </button>}
      </div>
    );
  }

  render() {
    const createGameWindow: JSX.Element | null = this.state.show_create_game ? this.createGameWindow() : null;
    const joinDiv: JSX.Element | null = this.state.show_create_game ? null : this.createJoinDiv();

    let infoBox: JSX.Element | null;
    if (this.state.info_box_message === null) {
      infoBox = null;
    } else {
      infoBox = <InfoBox message={this.state.info_box_message} />;
    }

    return (
      <div className="App" >
        <header className="App-header"> games.mickjohn.com </header>
        {infoBox}
        {joinDiv}
        {createGameWindow}
      </div >
    );
  }
}

export default App;
