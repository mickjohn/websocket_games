var websocket = null;
const websocket_endpoint = "redorblack"
const websocket_port = "8080";
var protocol;
var redirecting = false;
const websocket_url = "ws://localhost:8080/redorblack";

if (window.location.hostname === "127.0.0.1"
    || window.location.hostname === "localhost") {
    protocol = "ws";
} else {
    protocol = "wss";
}

/* Websocket functions */
function onOpen(e) {
    console.info(`Connection has been opened`);
    set_connection_status();
}
/* END Websocket functions */

function redirectHome() {
    if (!redirecting) {
        let location = window.location;
        let protocol = location.protocol;
        let host = location.host;
        let url = `${protocol}//${host}/`;
        redirecting = true;
        window.location.href = url;
    }
}

function createWebsocketConnection(url) {
    if (websocket === null || websocket.readyState === WebSocket.CLOSED) {
        console.info("Creating websocket connection");
        websocket = new WebSocket(url);
        websocket.onopen = function (event) {
            onOpen(event);
        };
        return true;
    } else {
        console.warn(`Not creating websocket connection. state is ${websocker.readyState}`);
        return false;
    }
}

function set_connection_status() {
    let msg = "Not connected";
    if (websocket === null) {
        msg = "Not connected";
    } else if (websocket.readyState === WebSocket.CLOSED) {
        msg = "Not connected";
    } else if (websocket.readyState === WebSocket.OPEN) {
        msg = "Websocket connected";
    }

    $("#connection-status-msg").text(msg);
}

function getJoinCode() {
    let params = new URLSearchParams(document.location.search.substring(1));
    return params.get("gameCode");
}

function init() {
    let code = getJoinCode();
    if (code === null) {
        console.error("No code in URL params, redirecting back to index");
        redirectHome();
    } else {
        console.info("Found required URL params. Creating websocket connection");
        createWebsocketConnection(websocket_url);
    }
}


if (!redirecting) {
    $(document).ready(function () {
        init();
    })
}

/* MESSAGES */