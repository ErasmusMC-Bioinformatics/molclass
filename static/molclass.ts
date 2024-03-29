// holds the logs recieved from the server
let logs = [];

// holds the current variant meta data
let variant = new Map<string, string>();

// holds the selected 'new search' meta data
let new_search = new Map<string, string>();
let new_search_elements = new Map<string, HTMLElement>();

// should be called right after the page loads to connect back to the server
function connect(): void {
    let ws_url_input = document.getElementById("ws_url") as HTMLInputElement;
    console.log(ws_url_input.value)
    let ws = new WebSocket(ws_url_input.value);
    ws.onopen = onConnect;
    ws.onmessage = onMessage;
    ws.onerror = onError;
    ws.onclose = onClose;
}

/* Molclass stores search history in localStorage as a json string
History is structured like this:
{
    "searches": [
        {"s": "NM1234:c.567C>T","dt": 1682429554664},
        {"s": "NM4321:c.765C>T","dt": 1682422738282}
    ]
}
*/
function initHistory(): void {
    let _history = localStorage.getItem("history");
    if (_history === null) {
        return;
    }

    // the html element to push the history to
    let tbody = document.getElementById("history-tbody") as HTMLElement;
    tbody.innerHTML = "";

    // create new rows for each previous search and add them to the 'tbody'
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

// Add 'search' to the search history in localStorage
// limiting the history to 30 searches
function addSearchToHistory(search): void {
    var _history = localStorage.getItem("history");
    if (_history === null) {
        _history = '{"searches": []}';
    }
    let history = JSON.parse(_history);
    let searches = history["searches"] as Array<object>;
    searches.push({"s": search, "dt": Date.now()});
    searches = searches.splice(-30);
    history["searches"] = searches;
    console.log(history);
    localStorage.setItem("history", JSON.stringify(history));
}

// called when there is a succesful websocket connection established
function onConnect(event: any): void {
    console.log("Websocket connected");

    let search_input = document.getElementById("search") as HTMLInputElement;
    let search = search_input.value;
    addSearchToHistory(search)
}

// called each time the server sends some data to the client over the websocket connection
// the 'event' is then passed on the the appropriate follow up function
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

// handles the log messages sent from the server, logging them to the console
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


// handles recieving new variant meta data
// also displays the gene/transcript/cdot/pdot values in their html elements
function updateVariant(message: any): void {
    let new_variant_data = message.data;
    variant.clear()
    console.debug("Variant", new_variant_data);
    for (let [key, value] of Object.entries(new_variant_data)){
        variant.set(key as string, value as string);

        // simply check if there is an html element with this keys ID
        // which there are for 'gene_variant', 'transcript_variant', etc
        let variant_elem = document.getElementById(`${key}_variant`);
        if (variant_elem){
            if (!variant_elem.innerHTML.includes(value as string)){
                variant_elem.innerHTML = value as string;
            }
        }
    }
}

// handles updating the source cards
// the server just sends pure HTML as data, so this just sets the card with this data
function updateSource(message: any): void {
    let source_name = message.name;
    let source_div = document.getElementById(`${source_name}_div`);

    source_div.innerHTML = message.data;
    initTooltips(source_div);
}


// checks if there are sources that disagree with the consensus
// if so, color the html yellow to let the user know
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

// handles the user constructing a new search from variant meta data
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

// creates/updates the consensus overview
// for every key in 'includeSet' it displays the different variant meta datas and what sources agree on them
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

// shouldn't happen, but handles an unexpected error with the websocket connection
function onError(event: any): void {
    console.log(JSON.stringify(event.data));
}

// if the server is done with sending data it closes the connection
// handle it here and set some leftover values
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

// init the bootstrap tooltip callbacks
function initTooltips(parent: HTMLElement): void {
    const tooltipTriggerList = parent.querySelectorAll('[data-bs-toggle="tooltip"]')
    //@ts-ignore
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
}

document.addEventListener('DOMContentLoaded', connect, false);
document.addEventListener('DOMContentLoaded', initHistory, false);