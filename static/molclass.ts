let logs = [];

function connect(): void {
    let ws_url_input = document.getElementById("ws_url") as HTMLInputElement;
    console.log(ws_url_input.value)
    let ws = new WebSocket(ws_url_input.value);
    ws.onopen = onConnect;
    ws.onmessage = onMessage;
    ws.onerror = onError;
    ws.onclose = onClose;
}

function onConnect(event: any): void {
    console.log("Websocket connected");
}

function onMessage(event: any): void {
    let message = JSON.parse(event.data);
    if (message.type == "log"){
        logMessage(message)
    } else if (message.type == "update"){
        updateMessage(message);
    }
}

function logMessage(message: any): void {
    message.messages.forEach( (message) => {
        console.log(message)
    });
    logs.push(message);
}

function updateMessage(message: any): void {
    let source_name = message.name;
    let source_div = document.getElementById(`${source_name}_div`);
    source_div.innerHTML = message.data;
}

function onError(event: any): void {
    console.log(JSON.stringify(event.data));
}

function onClose(event: any): void {
    var source_elements = document.querySelectorAll('[data-source-loading]');
    [].forEach.call(source_elements, function(element) {
        element.innerHTML = "<p>Could not load source</p>";
    });
    console.log(logs)
}

document.addEventListener('DOMContentLoaded', connect, false);