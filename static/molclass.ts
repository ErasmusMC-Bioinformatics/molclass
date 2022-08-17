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

function initHistory(): void {
    let _history = localStorage.getItem("history");
    if (_history === null) {
        return;
    }
    let tbody = document.getElementById("history-tbody") as HTMLElement;
    tbody.innerHTML = "";
    let history = JSON.parse(_history);
    [].forEach.call(history.searches, function(s_dt) {
        let search = s_dt.s;
        let datetime = new Date(s_dt.dt);
        let tr = document.createElement("tr");
        let dt = document.createElement("td");

        let _minutes = datetime.getMinutes();
        let minutes = `${_minutes}`;
        if (_minutes < 10){
            minutes = `0${_minutes}`;
        }

        dt.innerHTML = `${datetime.getFullYear()}-${datetime.getMonth()}-${datetime.getDate()} ${datetime.getHours()}:${minutes}`;
        tr.appendChild(dt);

        let s = document.createElement("td");
        let a = document.createElement("a");
        a.href = `/search?search=${search}`;
        a.innerHTML = search;
        s.appendChild(a)
        tr.appendChild(s)

        tbody.appendChild(tr);
    });
}

function addSearchToHistory(search): void {
    var _history = localStorage.getItem("history");
    if (_history === null) {
        _history = '{"searches": []}';
    }
    let history = JSON.parse(_history);
    let searches = history["searches"] as Array<object>;
    searches.push({"s": search, "dt": Date.now()});
    localStorage.setItem("history", JSON.stringify(history));
}

function onConnect(event: any): void {
    console.log("Websocket connected");

    let search_input = document.getElementById("search") as HTMLInputElement;
    let search = search_input.value;
    addSearchToHistory(search)
}

function onMessage(event: any): void {
    let message = JSON.parse(event.data);
    if (message.type == "log"){
        logMessage(message.messages)
    } else if (message.type == "update"){
        updateSource(message);
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

function updateSource(message: any): void {
    let source_name = message.name;
    let source_div = document.getElementById(`${source_name}_div`);

    source_div.innerHTML = message.data;
    if (message.found){
        source_div.style.opacity = "1.0";
    } else {
        source_div.style.opacity = "0.5";
    }
    
    if (message.timeout){
        let card_subtitle = source_div.querySelector(".card-subtitle") as HTMLElement;
        card_subtitle.innerHTML = `Timeout <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" class="bi bi-clock" viewBox="0 0 16 16"><path d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z"/><path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z"/></svg>`;
        source_div.style.opacity = "0.5";
    }
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
    let asArray = Array.from(new_search.values())
    let search = asArray.join(" ");
    let new_search_div = document.getElementById("new_search_link_div");
    if (asArray.length == 0){
        new_search_div.innerHTML = `-`;
    } else {
        new_search_div.innerHTML = `<a href="/search?search=${search}">${search}</a>`;
    }
}

function updateConsensus(message: any): void {
    let key_values: Object = message.data;
    
    let consensusChecks = ["gene", "transcript", "cdot", "pdot"];

    [].forEach.call(consensusChecks, function(check_key) {
        if (key_values.hasOwnProperty(check_key)){
            checkConsensus(key_values[check_key], check_key)
        }
    });

    let includeSet = new Set(["transcript", "cdot", "pdot", "gene", "ref", "alt"]);

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
document.addEventListener('DOMContentLoaded', initHistory, false);