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
    var date = Date.now();
    var currentMessages = messagesTextArea.val();
    var newMsg = `${currentMessages}\n${date} : ${message}`;
    messagesTextArea.val(newMsg);
}

window.addEventListener("load", init, false);

function _create_game_data() {
    var data = {
        "type": "CreateGame",
    };
    messageToSend.val(JSON.stringify(data, null, 2));
}

function _add_user_data() {
    username = $('#add_player_username').val();
    game_id = $('#add_player_game_id').val();
    var data = {
        "game_id": `${game_id}`,
        "type": "AddPlayer",
        "username": `${username}`
    };
    messageToSend.val(JSON.stringify(data, null, 2));
}

function _add_register_player_data() {
    game_id = $('#register_player_game_id').val();
    username = $('#register_player_username').val();
    var data = {
        "type": "Register",
        "username": `${username}`,
        "game_id": `${game_id}`,
    };
    messageToSend.val(JSON.stringify(data, null, 2));
}

function _add_activate_id_data() {
    game_id = $('#activate_id_game_id').val();
    user_id = $('#activate_id_user_id').val();
    var data = {
        "type": "Activate",
        "user_id": `${user_id}`,
        "game_id": `${game_id}`,
    };
    messageToSend.val(JSON.stringify(data, null, 2));
}

function _add_start_game_data() {
    game_id = $('#start_game_game_id').val();
    user_id = $('#start_game_owner_id').val();
    var data = {
        "type": "StartGame",
        "user_id": `${user_id}`,
        "game_id": `${game_id}`,
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
    const game_id = $('#activate_id_game_id').val();
    const user_id = $('#activate_id_user_id').val();
    const url = `http://localhost:3000?game_id=${game_id}&uid=${user_id}`;
    $('#open_react_link').attr("href", url);
}

function updateFieldsHelper(msg) {
    let obj = JSON.parse(msg);
    if (obj['type'] === 'GameCreated') {
        let id = obj['game_code'];
        $('#activate_id_game_id').val(id);
        $('#register_player_game_id').val(id);
        $('#start_game_game_id').val(id);
        $('#add_player_game_id').val(id);
    } else if (obj['type'] === 'Registered') {
        let uid = obj['user_id'];
        $('#activate_id_user_id').val(uid);
        $('#start_game_owner_id').val(uid);
    }
}