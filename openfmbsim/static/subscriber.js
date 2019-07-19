
/*
 * Copyright 2019 Smarter Grid Solutions
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * Add a new definition into the specified table.
 * @param {Element} parent The table to insert into.
 * @param {string} name The name of the value that is being added.
 * @param {any} value The value that is being added.
 */
var addDefinition = function (parent, name, value) {
    var tr = document.createElement("tr");
    var tdName = document.createElement("td");
    tdName.textContent = name;

    var tdValue = document.createElement("td");
    tdValue.textContent = value

    tr.appendChild(tdName);
    tr.appendChild(tdValue);
    parent.appendChild(tr);
}

/**
 * Add a list of simple values into the table.
 * @param {Element} parent The parent table to insert into.
 * @param {object} values Object of values to insert. These values are JSON
 *                        objects following the normal OpenFMB structure.
 */
var addValuesDefinition = function (parent, values) {
    Object.keys(values).forEach(function (key) {
        var units = values[key].units.value;
        if (units && units.startsWith("UnitSymbolKind_")) {
            units = " " + units.substr(15);
        }
        // If the value is the default, then it is omitted
        var value = values[key].actVal || 0
        addDefinition(parent, key, "" + value + units);
    })
}

/**
 * Add a list of values into the table where each value will have phase
 * measurements.
 * @param {Element} parent The parent table to insert into.
 * @param {object} values Object of phase values to insert.
 */
var addPhaseValuesDefinition = function (parent, values) {
    Object.keys(values).forEach(function (key) {
        var phaseValues = values[key]
        Object.keys(phaseValues).forEach(function (phase) {
            var units = phaseValues[phase].units && phaseValues[phase].units.SIUnit || "";
            if (units && units.startsWith("UnitSymbolKind_")) {
                units = " " + units.substr(15);
            }
            if (phaseValues[phase].hasOwnProperty("cVal")) {
                addDefinition(parent, key + " " + phase, "" + phaseValues[phase].cVal.mag.f + "∠" + phaseValues[phase].cVal.ang.f + units);
            }
        })
    })
}

/**
 * Creates the entire definition for an object. This is a table element that
 * can be hosted in something else. In this way, we just replace the entire
 * table when we have new data for an object.
 * @param {object} evtData The message data that was received.
 */
var createDeviceDefinition = function(evtData) {
    var itemDefs = document.createElement("table");
    var iedMrid = evtData.ied.identifiedObject.mRID;
    itemDefs.id = iedMrid + "-defs";

    addDefinition(itemDefs, "IED MRID", iedMrid);

    var msgDate = new Date(0);
    msgDate.setUTCSeconds(parseInt(evtData.readingMessageInfo.messageInfo.messageTimeStamp.seconds));
    addDefinition(itemDefs, "Message date", msgDate);
    addValuesDefinition(itemDefs, evtData.generationReading.readingMMTR);
    addPhaseValuesDefinition(itemDefs, evtData.generationReading.readingMMXU);

    return itemDefs;
}

/**
 * Handle new data for a device. This can either add the device to the list
 * or update an existing device.
 * @param {object} evtData The OpenFMB data that was received.
 */
var addOrUpdate = function(evtData) {
    var devices = document.getElementById("devices");

    // Which node with the devices table do we want to add this to?
    // Get the ID of the associated IED
    var iedMrid = evtData.ied.identifiedObject.mRID

    // Do we have a node for this already? If not, we create it and add it now
    var iedElem = document.getElementById(iedMrid);
    var oldDlElem = document.getElementById(iedMrid + "-defs");
    if (!iedElem) {
        // Create the data element for this item
        var iedElem = document.createElement("h5");
        iedElem.id = iedMrid
        var iedHeading = document.createElement("div");
        iedHeading.className = "row";
        var nameElem = document.createElement("div");
        nameElem.textContent = iedMrid;
        nameElem.className = "seven columns";
        iedHeading.appendChild(nameElem);

        var deleteElem = document.createElement("button");
        deleteElem.textContent = "Delete";
        deleteElem.className = "two columns";
        deleteElem.addEventListener("click", deleteDevice);
        deleteElem.setAttribute("data-mrid", iedMrid);
        iedHeading.appendChild(deleteElem);

        iedElem.appendChild(iedHeading);

        // And create the empty definition list for this item
        oldDlElem = document.createElement("table");
        iedElem.appendChild(oldDlElem);
        devices.appendChild(iedElem);
    }

    // Handle the update by creating the new definition list and then replacing
    // the one in the iedElem
    var newDlElem = createDeviceDefinition(evtData);
    iedElem.replaceChild(newDlElem, oldDlElem)
}

/**
 * Callback to request a new device created.
 */
var createNewDevice = function() {
    fetch("/devices", { method: "POST" })
        .then(response => {
            console.log("Created device");
        })
        .catch(error => {
            console.log(error)
        })
}

/**
 * Callback to delete an existing device.
 */
var deleteDevice = function(event) {
    var iedMrid = event.target.getAttribute("data-mrid");

    fetch("/devices/" + iedMrid, { method: "DELETE" })
        .then(response => {
            console.log("Deleted device");
            // If we are successful, then remove the node.
            var devices = document.getElementById("devices");
            var iedElem = document.getElementById(iedMrid);
            if (iedElem) {
                devices.removeChild(iedElem);
            }
        })
        .catch(error => {
            console.log(error)
        })
}

document.addEventListener("DOMContentLoaded", function() {
    // Subscribe to server sent events
    var evtSource = new EventSource("/sse");
    evtSource.onmessage = function(e) {
        var evtData = JSON.parse(e.data);
        addOrUpdate(evtData);
    };

    // Connect the UI buttons for devices
    document.getElementById("create-device").addEventListener("click", createNewDevice);
});
