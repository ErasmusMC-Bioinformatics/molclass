var logs = [];
var variant = new Map();
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
function updateConsensus(message) {
    var key_values = message.data;
    var consensusChecks = ["gene", "transcript", "cdot", "pdot"];
    [].forEach.call(consensusChecks, function (check_key) {
        if (key_values.hasOwnProperty(check_key)) {
            checkConsensus(key_values[check_key], check_key);
        }
    });
    var includeSet = new Set(["transcript", "cdot", "pdot", "gene"]);
    var variant_data_elem = document.getElementById("variant-data-div");
    variant_data_elem.innerHTML = "";
    var variant_data_template = document.getElementById("variant-data-template");
    for (var _i = 0, _a = Object.entries(key_values); _i < _a.length; _i++) {
        var _b = _a[_i], key = _b[0], values = _b[1];
        if (!includeSet.has(key)) {
            continue;
        }
        var template = variant_data_template.content.cloneNode(true);
        var table = template.querySelectorAll("table")[0];
        var caption = template.querySelectorAll("caption")[0];
        caption.innerHTML = key;
        var tbody = template.querySelectorAll("tbody")[0];
        for (var _c = 0, _d = Object.entries(values); _c < _d.length; _c++) {
            var _e = _d[_c], value = _e[0], sources = _e[1];
            var tr = document.createElement("tr");
            var tdValue = document.createElement("td");
            tdValue.innerHTML = value;
            var tdSources = document.createElement("td");
            tdSources.innerHTML = sources.join("<br />");
            tr.appendChild(tdValue);
            tr.appendChild(tdSources);
            tbody.appendChild(tr);
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
