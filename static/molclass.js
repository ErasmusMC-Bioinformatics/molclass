var logs = [];
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
    var message = JSON.parse(event.data);
    if (message.type == "log") {
        logMessage(message);
    }
    else if (message.type == "update") {
        updateMessage(message);
    }
}
function logMessage(message) {
    logs.push(message);
}
function updateMessage(message) {
    var source_name = message.name;
    var source_div = document.getElementById(source_name + "_div");
    source_div.innerHTML = message.data;
}
function onError(event) {
    console.log(JSON.stringify(event.data));
}
function onClose(event) {
    var source_elements = document.querySelectorAll('[data-source-loading]');
    [].forEach.call(source_elements, function (element) {
        element.innerHTML = "<p>Could not load source</p>";
    });
}
document.addEventListener('DOMContentLoaded', connect, false);
