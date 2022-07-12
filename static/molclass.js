function connect() {
    var ws_url_input = document.getElementById("ws_url");
    console.log(ws_url_input.value);
    var ws = new WebSocket(ws_url_input.value);
    ws.onopen = onConnect;
    ws.onmessage = onMessage;
    ws.onerror = onError;
    ws.onclose = onClose;
}
function onConnect(event) {
    console.log("Websocket connected");
}
function onMessage(event) {
    console.log(event);
}
function onError(event) {
    console.log(JSON.stringify(event.data));
}
function onClose(event) {
    console.log("Websocket closed");
}
document.addEventListener('DOMContentLoaded', connect, false);
