var __spreadArrays = (this && this.__spreadArrays) || function () {
    for (var s = 0, i = 0, il = arguments.length; i < il; i++) s += arguments[i].length;
    for (var r = Array(s), k = 0, i = 0; i < il; i++)
        for (var a = arguments[i], j = 0, jl = a.length; j < jl; j++, k++)
            r[k] = a[j];
    return r;
};
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
function initHistory() {
    var _history = localStorage.getItem("history");
    if (_history === null) {
        return;
    }
    var tbody = document.getElementById("history-tbody");
    tbody.innerHTML = "";
    var history = JSON.parse(_history);
    [].forEach.call(history.searches, function (s_dt) {
        var search = s_dt.s;
        var datetime = new Date(s_dt.dt);
        var tr = document.createElement("tr");
        var dt = document.createElement("td");
        var _minutes = datetime.getMinutes();
        var minutes = "" + _minutes;
        if (_minutes < 10) {
            minutes = "0" + _minutes;
        }
        dt.innerHTML = datetime.getFullYear() + "-" + datetime.getMonth() + "-" + datetime.getDate() + " " + datetime.getHours() + ":" + minutes;
        tr.appendChild(dt);
        var s = document.createElement("td");
        var a = document.createElement("a");
        a.href = "/search?search=" + search;
        a.innerHTML = search;
        s.appendChild(a);
        tr.appendChild(s);
        tbody.appendChild(tr);
    });
}
function addSearchToHistory(search) {
    var _history = localStorage.getItem("history");
    if (_history === null) {
        _history = '{"searches": []}';
    }
    var history = JSON.parse(_history);
    var searches = history["searches"];
    searches.push({ "s": search, "dt": Date.now() });
    searches = searches.splice(-30);
    history["searches"] = searches;
    console.log(history);
    localStorage.setItem("history", JSON.stringify(history));
}
function onConnect(event) {
    console.log("Websocket connected");
    var search_input = document.getElementById("search");
    var search = search_input.value;
    addSearchToHistory(search);
}
function onMessage(event) {
    var message = JSON.parse(event.data);
    if (message.type == "log") {
        logMessage(message.messages);
    }
    else if (message.type == "update") {
        updateSource(message);
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
    variant.clear();
    console.debug("Variant", new_variant_data);
    for (var _i = 0, _a = Object.entries(new_variant_data); _i < _a.length; _i++) {
        var _b = _a[_i], key = _b[0], value = _b[1];
        variant.set(key, value);
        var variant_elem = document.getElementById(key + "_variant");
        if (variant_elem) {
            if (!variant_elem.innerHTML.includes(value)) {
                variant_elem.innerHTML = value;
            }
        }
    }
}
function updateSource(message) {
    var source_name = message.name;
    var source_div = document.getElementById(source_name + "_div");
    source_div.innerHTML = message.data;
    initTooltips(source_div);
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
    var asArray = Array.from(new_search.values());
    var search = asArray.join(" ");
    var new_search_div = document.getElementById("new_search_link_div");
    if (asArray.length == 0) {
        new_search_div.innerHTML = "-";
    }
    else {
        new_search_div.innerHTML = "<a href=\"/search?search=" + search + "\">" + search + "</a>";
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
function initTooltips(parent) {
    var tooltipTriggerList = parent.querySelectorAll('[data-bs-toggle="tooltip"]');
    //@ts-ignore
    var tooltipList = __spreadArrays(tooltipTriggerList).map(function (tooltipTriggerEl) { return new bootstrap.Tooltip(tooltipTriggerEl); });
}
document.addEventListener('DOMContentLoaded', connect, false);
document.addEventListener('DOMContentLoaded', initHistory, false);
