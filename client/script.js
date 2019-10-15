var wsUri = "ws://127.0.0.1:8080";
var output;
var websocketConn = null;

var connectButton = null;
var disconnectButton = null;
var submitMessageButton = null
var clearMessagesButton = null;
var messagesTextArea = null;
var websockerUrl = null;
var messageToSend = null;

var game_id = 'NA';

function init() {
    console.log("Init");
    connectButton = $('#websocket_connect');
    disconnectButton = $('#websocket_disconnect');
    submitMessageButton = $('#submit_message');
    clearMessagesButton = $('#clear_messages');
    messagesTextArea = $('#messages');
    websockerUrl = $('#websocket_url');
    messageToSend = $('#submit_message_textbox');

    connectButton.click(function () {
        console.log("Connect button clicked");
        var addr = websockerUrl.val();
        createWebsocket(addr);
    });

    disconnectButton.click(function () {
        console.log("Closing websocket");
        websocketConn.close();
        websocketConn = null;
    });

    submitMessageButton.click(function () {
        if (websocketConn !== null) {
            var msg = messageToSend.val();
            websocketConn.send(msg);
        }
    });

    clearMessagesButton.click(function () {
        messagesTextArea.val('');
    });

    // Set URL Buttons
    $('#red_or_black_url').click(function () { _set_url_endpoint('RedOrBlack'); });

    // Helper Buttons
    $('#send_debug_button').click(function () {
        if (websocketConn !== null) {
            websocketConn.send('{"type": "Debug"}');
            writeMessage('DEBUG sent');
        }
    });

    $('#create_game_button').click(function () { _create_game_data(); });
    $('#add_player_button').click(function () { _add_user_data(); });
    $('#register_player_button').click(function () { _add_register_player_data(); });
    $('#activate_id_button').click(function () { _add_activate_id_data(); });
    $('#start_game_button').click(function () { _add_start_game_data(); });
    $('#make_guess_button').click(function () { _add_make_guess_data(); });

    $("#open_react_link").on('click', function (e) {
        _set_react_url();
    });

}

function createWebsocket(addr) {
    if (websocketConn === null) {
        console.log("Opening new websocket connection");
        websocketConn = new WebSocket(addr);
        websocketConn.onopen = function (evt) { onOpen(evt) };
        websocketConn.onclose = function (evt) { onClose(evt) };
        websocketConn.onmessage = function (evt) { onMessage(evt) };
        websocketConn.onerror = function (evt) { onError(evt) };
    } else {
        console.log("Websocket connection already exists, not creating new one");
        writeMessage("websocket connection already open, disconnect first");
    }
}

function onOpen(evt) {
    writeMessage("CONNECTED");
}

function onClose(evt) {
    writeMessage("DISCONNECTED");
    websocketConn = null;
}

function onMessage(evt) {
    writeMessage(evt.data);
    updateFieldsHelper(evt.data);
    console.log(`message = ${evt.data}`)
}

function onError(evt) {
    writeMessage(evt.data);
}

function writeMessage(message) {
    let date = Date.now();
    let currentMessages = messagesTextArea.val();
    let newMsg = `${currentMessages}\n${date} : ${message}`;
    messagesTextArea.val(newMsg);
}

window.addEventListener("load", init, false);

function _create_game_data() {
    var data = {
        "type": "CreateGame",
    };
    messageToSend.val(JSON.stringify(data, null, 2));
}

function _add_register_player_data() {
    let username = $('#register_player_username').val();
    let data = {
        "type": "Register",
        "username": `${username}`,
    };
    messageToSend.val(JSON.stringify(data, null, 2));
}

function _add_activate_id_data() {
    let user_id = $('#activate_id_user_id').val();
    let data = {
        "type": "Activate",
        "user_id": `${user_id}`,
    };
    messageToSend.val(JSON.stringify(data, null, 2));
}

function _add_start_game_data() {
    let user_id = $('#start_game_owner_id').val();
    let data = {
        "type": "StartGame",
        "user_id": `${user_id}`,
    };
    messageToSend.val(JSON.stringify(data, null, 2));
}

function _add_make_guess_data() {
    let guess = $("input[type='radio'][name='guess']:checked").val();
    let data = {
        "type": "PlayTurn",
        "guess": `${guess}`
    };
    messageToSend.val(JSON.stringify(data, null, 2));
}

function _set_url_endpoint(endpoint) {
    url_text = $('#websocket_url').val()
    url = new URL(url_text)
    port = ''
    if (url.port != '') {
        port = `:${url.port}`
    }
    new_url = `${url.protocol}//${url.hostname}${port}/${endpoint}`
    $('#websocket_url').val(new_url)
}

function _set_react_url() {
    const user_id = $('#activate_id_user_id').val();
    const url = `http://localhost:3000?game_id=${game_id}&uid=${user_id}`;
    $('#open_react_link').attr("href", url);
}

function updateFieldsHelper(msg) {
    let obj = JSON.parse(msg);
    if (obj['type'] === 'GameCreated') {
        let id = obj['game_code'];
        game_id = id;
        _set_url_endpoint(`game_${id}`);
    } else if (obj['type'] === 'Registered') {
        let uid = obj['user_id'];
        $('#activate_id_user_id').val(uid);
        $('#start_game_owner_id').val(uid);
        $('#make_guess_player_id').val(uid);
    }
}