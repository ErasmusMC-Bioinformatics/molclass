let logs = [];
let variant = new Map<string, string>();
let new_search = new Map<string, string>();
let new_search_elements = new Map<string, HTMLElement>();

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
    } else if (message.type == "consensus"){
        updateConsensus(message);
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
    console.debug("Variant", new_variant_data);
    for (let [key, value] of Object.entries(new_variant_data)){
        variant[key]=value;
        let variant_elem = document.getElementById(`${key}_variant`);
        if (variant_elem){
            if (!variant_elem.innerHTML.includes(value as string)){
                variant_elem.innerHTML = value as string;
            }
        }
    }
}

function updateMessage(message: any): void {
    let source_name = message.name;
    let source_div = document.getElementById(`${source_name}_div`);
    source_div.innerHTML = message.data;
}

function checkConsensus(data: Map<string, Map<string, Array<string>>>, element_key: string){
    let value_element_id = `${element_key}_variant`;
    let value_elem = document.getElementById(value_element_id) as HTMLElement;
    if (value_elem == null){
        console.warn(`Could not find ${value_element_id}`);
        return
    }
    if (value_elem.classList.contains("btn")){
        return // already checked
    }
    if (Object.keys(data).length == 1) {
        let [value] = Object.keys(data);
        let sameValue = decodeURI(value_elem.innerText).includes(decodeURI(value));
        if (sameValue){
            value_elem.classList.toggle("btn");
            value_elem.classList.toggle("btn-outline-success");
            value_elem.classList.toggle("btn-lg");
        } else {
            value_elem.classList.toggle("btn");
            value_elem.classList.toggle("btn-outline-warning");
            value_elem.classList.toggle("btn-lg");
        }
    } else {
        value_elem.classList.toggle("btn");
        value_elem.classList.toggle("btn-outline-warning");
        value_elem.classList.toggle("btn-lg");
    }
}

function updateNewSearch(elem: HTMLElement, key: string, value: string): void {
    var removeKey = false;
    if (new_search_elements.has(key)){ // already selected key
        let old_elem = new_search_elements.get(key);
        old_elem.classList.remove("new-search-selected");
        if (elem == old_elem){
            new_search.delete(key);
            new_search_elements.delete(key);
            removeKey = true;
        }
    }
    if(!removeKey){
        new_search.set(key, value);
        new_search_elements.set(key, elem);
        elem.classList.toggle("new-search-selected");
        
    }
    let search = Array.from(new_search.values()).join(" ");
    let new_search_div = document.getElementById("new_search_link_div");
    new_search_div.innerHTML = `<a href="/search?search=${search}">${search}</a>`;
}

function updateConsensus(message: any): void {
    let key_values: Object = message.data;
    
    let consensusChecks = ["gene", "transcript", "cdot", "pdot"];

    [].forEach.call(consensusChecks, function(check_key) {
        if (key_values.hasOwnProperty(check_key)){
            checkConsensus(key_values[check_key], check_key)
        }
    });

    let includeSet = new Set(["transcript", "cdot", "pdot", "gene"]);

    let variant_data_elem  = document.getElementById("variant-data-div");
    variant_data_elem.innerHTML = "";
    let variant_data_template = document.getElementById("variant-data-template") as HTMLTemplateElement;
    for (let [key, values] of Object.entries(key_values)) {
        if (!includeSet.has(key)){
            continue;
        }
        let template = variant_data_template.content.cloneNode(true) as HTMLElement;
        let table = template.querySelectorAll("table")[0];
        let caption = template.querySelectorAll("caption")[0];
        caption.innerHTML = key;
        let tbody = template.querySelectorAll("tbody")[0];
        

        for (let [value, sources] of Object.entries(values)){
            let tr = document.createElement("tr");

            let tdValue = document.createElement("td");
            tdValue.innerHTML = value;
            tdValue.onclick = function(ev) {updateNewSearch(tdValue, key, value);}
            tdValue.style.cursor = "pointer";

            let tdSources = document.createElement("td");
            tdSources.innerHTML = (sources as Array<string>).join("<br />");

            tr.appendChild(tdValue);
            tr.appendChild(tdSources);
            tbody.appendChild(tr);
        }

        table.parentElement.classList.toggle("border")
        if (Object.keys(values).length == 1) {
            table.parentElement.classList.toggle("border-success")
            table.parentElement.classList.toggle("border-2")
        } else {
            table.parentElement.classList.toggle("border-warning")
            table.parentElement.classList.toggle("border-4")
        }
        variant_data_elem.appendChild(template)
    }
    console.log("Consensus", key_values);
}

function onError(event: any): void {
    console.log(JSON.stringify(event.data));
}

function onClose(event: any): void {
    var source_elements = document.querySelectorAll('[data-source-loading]');
    [].forEach.call(source_elements, function(element) {
        element.innerHTML = "<p>Not found</p>";
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