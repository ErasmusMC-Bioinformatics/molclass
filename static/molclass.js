var logs = [];
var variant = new Map();
var new_search = new Map();
var new_search_elements = new Map();
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
        logMessage(message.messages);
    }
    else if (message.type == "update") {
        updateMessage(message);
    }
    else if (message.type == "variant") {
        updateVariant(message);
    }
    else if (message.type == "consensus") {
        updateConsensus(message);
    }
}
function logMessage(messages) {
    messages.forEach(function (message) {
        logs.push(message);
        switch (message.level) {
            case "debug":
                console.debug(message.source + ": " + message.message);
                break;
            case "info":
                console.info(message.source + ": " + message.message);
                break;
            case "warning":
                console.warn(message.source + ": " + message.message);
                break;
            case "error":
                console.error(message.source + ": " + message.message);
                break;
        }
    });
}
function updateVariant(message) {
    var new_variant_data = message.data;
    console.debug("Variant", new_variant_data);
    for (var _i = 0, _a = Object.entries(new_variant_data); _i < _a.length; _i++) {
        var _b = _a[_i], key = _b[0], value = _b[1];
        variant[key] = value;
        var variant_elem = document.getElementById(key + "_variant");
        if (variant_elem) {
            if (!variant_elem.innerHTML.includes(value)) {
                variant_elem.innerHTML = value;
            }
        }
    }
}
function updateMessage(message) {
    var source_name = message.name;
    var source_div = document.getElementById(source_name + "_div");
    source_div.innerHTML = message.data;
    if (!message.found) {
        source_div.style.opacity = "0.5";
    }
}
function checkConsensus(data, element_key) {
    var value_element_id = element_key + "_variant";
    var value_elem = document.getElementById(value_element_id);
    if (value_elem == null) {
        console.warn("Could not find " + value_element_id);
        return;
    }
    if (value_elem.classList.contains("btn")) {
        return; // already checked
    }
    if (Object.keys(data).length == 1) {
        var value = Object.keys(data)[0];
        var sameValue = decodeURI(value_elem.innerText).includes(decodeURI(value));
        if (sameValue) {
            value_elem.classList.toggle("btn");
            value_elem.classList.toggle("btn-outline-success");
            value_elem.classList.toggle("btn-lg");
        }
        else {
            value_elem.classList.toggle("btn");
            value_elem.classList.toggle("btn-outline-warning");
            value_elem.classList.toggle("btn-lg");
        }
    }
    else {
        value_elem.classList.toggle("btn");
        value_elem.classList.toggle("btn-outline-warning");
        value_elem.classList.toggle("btn-lg");
    }
}
function updateNewSearch(elem, key, value) {
    var removeKey = false;
    if (new_search_elements.has(key)) { // already selected key
        var old_elem = new_search_elements.get(key);
        old_elem.classList.remove("new-search-selected");
        if (elem == old_elem) {
            new_search["delete"](key);
            new_search_elements["delete"](key);
            removeKey = true;
        }
    }
    if (!removeKey) {
        new_search.set(key, value);
        new_search_elements.set(key, elem);
        elem.classList.toggle("new-search-selected");
    }
    var search = Array.from(new_search.values()).join(" ");
    var new_search_div = document.getElementById("new_search_link_div");
    if (search.length == 0) {
        new_search_div.innerHTML = "<a href=\"/search?search=" + search + "\">" + search + "</a>";
    }
    else {
        new_search_div.innerHTML = "-";
    }
}
function updateConsensus(message) {
    var key_values = message.data;
    var consensusChecks = ["gene", "transcript", "cdot", "pdot"];
    [].forEach.call(consensusChecks, function (check_key) {
        if (key_values.hasOwnProperty(check_key)) {
            checkConsensus(key_values[check_key], check_key);
        }
    });
    var includeSet = new Set(["transcript", "cdot", "pdot", "gene", "ref", "alt"]);
    var variant_data_elem = document.getElementById("variant-data-div");
    variant_data_elem.innerHTML = "";
    var variant_data_template = document.getElementById("variant-data-template");
    var _loop_1 = function (key, values) {
        if (!includeSet.has(key)) {
            return "continue";
        }
        var template = variant_data_template.content.cloneNode(true);
        var table = template.querySelectorAll("table")[0];
        var caption = template.querySelectorAll("caption")[0];
        caption.innerHTML = key;
        var tbody = template.querySelectorAll("tbody")[0];
        var _loop_2 = function (value, sources) {
            var tr = document.createElement("tr");
            var tdValue = document.createElement("td");
            tdValue.innerHTML = value;
            tdValue.onclick = function (ev) { updateNewSearch(tdValue, key, value); };
            tdValue.style.cursor = "pointer";
            var tdSources = document.createElement("td");
            tdSources.innerHTML = sources.join("<br />");
            tr.appendChild(tdValue);
            tr.appendChild(tdSources);
            tbody.appendChild(tr);
        };
        for (var _i = 0, _a = Object.entries(values); _i < _a.length; _i++) {
            var _b = _a[_i], value = _b[0], sources = _b[1];
            _loop_2(value, sources);
        }
        table.parentElement.classList.toggle("border");
        if (Object.keys(values).length == 1) {
            table.parentElement.classList.toggle("border-success");
            table.parentElement.classList.toggle("border-2");
        }
        else {
            table.parentElement.classList.toggle("border-warning");
            table.parentElement.classList.toggle("border-4");
        }
        variant_data_elem.appendChild(template);
    };
    for (var _i = 0, _a = Object.entries(key_values); _i < _a.length; _i++) {
        var _b = _a[_i], key = _b[0], values = _b[1];
        _loop_1(key, values);
    }
    console.log("Consensus", key_values);
}
function onError(event) {
    console.log(JSON.stringify(event.data));
}
function onClose(event) {
    var source_elements = document.querySelectorAll('[data-source-loading]');
    [].forEach.call(source_elements, function (element) {
        element.innerHTML = "<p>Not found</p>";
        var source_name = element.dataset.sourceLoading;
        var source_div = document.getElementById(source_name + "_div");
        source_div.style.opacity = "0.3";
    });
    var spinners = document.querySelectorAll(".spinner-border");
    [].forEach.call(spinners, function (element) {
        element.remove();
    });
    console.log(logs);
}
document.addEventListener('DOMContentLoaded', connect, false);
