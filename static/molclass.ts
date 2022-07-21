let logs = [];
let variant = new Map<string, string>();

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
        logMessage(message.messages)
    } else if (message.type == "update"){
        updateMessage(message);
    } else if (message.type == "variant"){
        updateVariant(message);
    }
}

function logMessage(messages: any): void {
    messages.forEach( (message) => {
        logs.push(message);
        switch (message.level){
            case "debug":
                console.debug(`${message.source}: ${message.message}`)
                break
            case "info":
                console.info(`${message.source}: ${message.message}`)
                break
            case "warning":
                console.warn(`${message.source}: ${message.message}`)
                break
            case "error":
                console.error(`${message.source}: ${message.message}`)
                break
        }
    });
}

function updateVariant(message: any): void {
    let new_variant_data = message.data;
    console.debug(new_variant_data);
    for (let [key, value] of Object.entries(new_variant_data)){
        variant[key]=value;
        let variant_elem = document.getElementById(`${key}_variant`);
        if (variant_elem){
            variant_elem.innerHTML = value as string;
        }
    }
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
        let source_name = element.dataset.sourceLoading;
        let source_div = document.getElementById(`${source_name}_div`)
        source_div.style.opacity = "0.3";
    });
    var spinners = document.querySelectorAll(".spinner-border");
    [].forEach.call(spinners, function(element) {
        element.remove();
    });
    console.log(logs)
}

document.addEventListener('DOMContentLoaded', connect, false);