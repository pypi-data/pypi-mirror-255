"use strict";

// -----------------
// Gloabal variables
// -----------------
let autoRefreshInterval = 15000; //15 seconds
let refreshInterval = null;
let downloadUrl = null;
let lang = "en";

// ------------------------------------------
// Onload GET for dynamic contents, animation
// ------------------------------------------
window.onload = function() {
	stopRefresh();
	performGET('combo-command');
}

// ----------------------------------
// Info and error dialog close events
// ----------------------------------
document.getElementById("about-dialog-close").addEventListener("click", () => {
	document.getElementById("about-dialog").close();
});
document.getElementById("error-dialog-close").addEventListener("click", () => {
	document.getElementById("error-dialog").close();
});

// -----------------------------------------------
// Set preset command parameters to the text field
// -----------------------------------------------
function setCommand() {
	stopRefresh()
    	let val = document.getElementById('combo-command').value;
	if (val == null || val == "command") {
		let params1 = document.getElementById('params-command');
		params1.value = "";
	} else {
		performGET('combo-command', val);
	}
}

// ----------------
// Set auto-refresh
// ----------------
function setRefresh() {
    	if (document.getElementById('auto-refresh').checked) {
		performGET('table-data');
		document.getElementById('wait-dialog').showModal();
		refreshInterval = setInterval(
					function() {performGET('table-data', 'no-wait-dialog');},
					autoRefreshInterval
					);
    	} else {
		stopRefresh();
    	}
}
function stopRefresh() {
	document.getElementById('auto-refresh').checked = false;
	clearInterval(refreshInterval);
}

// -----------
// GET request
// -----------
function performGET(targetID, spec) {
	let url = null;
	if (targetID == "combo-command") {
		if (typeof(spec) == 'undefined') {
			spec = "web=list";
		} else {
			spec = "web=" + spec;
		}
		url = spec;
	} else if (targetID == "table-data") {
		let params1 = document.getElementById('params-command');
		url = "web=" + params1.value;
		if (typeof(spec) == 'undefined' || spec != 'no-wait-dialog') {
			document.getElementById('wait-dialog').showModal();
		}
	} else {
		respText = "Unknown targetID:<br><br>" + targetID;
		console.log('Error response', respText);
		document.getElementById("error-dialog-message").innerHTML = respText;
		document.getElementById("wait-dialog").close();
		document.getElementById("error-dialog").showModal();
		return;
	}
	let respStatus = 0;
	let respStatusText = 0;
	let respText = null;
	fetch(url,
		{
    		method: 'get',
    	  	headers: {
         	'Accept': 'application/json, text/plain, */*',
         	'Content-Type': 'text/html'
    	  	}
 	}).then(function(response) {
		respStatus = response.status;
	  	respStatusText = response.statusText;
	  	return response.text();
	}).then(function(data) {
		respText = data;
		document.getElementById("wait-dialog").close();
		if (respStatus == 200) {
			// --------
			// Set data
			// --------
			if (respText.startsWith("<!--lang=de-->")) {
				lang = "de"
			}
			let date = new Date();
			let currentDateTime = date.toLocaleString(lang);
			let label1 = document.getElementById('label-timestamp');
			label1.innerHTML = currentDateTime;
			if (targetID == "combo-command") {
				let combo1 = null;
				let params1 = null;
				if (spec == "web=list") {
					combo1 = document.getElementById('combo-command');
					combo1.innerHTML = respText;
					let params1 = document.getElementById('params-command');
					params1.value = "";
				} else {
					params1 = document.getElementById('params-command');
					params1.value = respText;
				}
			} else if (targetID == "table-data") {
				let table1 = document.getElementById('table-data');
				table1.innerHTML = respText;
				// ----------------
				// Play animation(s)
				// ----------------
				document.getAnimations().forEach((animation) => {
					if (animation.animationName == "fade") {
						animation.play();
					}
				});
			} else {
				//Should not occur here because of the element ID check above
			}
		} else {
			respText = respStatus + " " + respStatusText + "<br><br>" + respText;
			console.log('Error response', respText);
			document.getElementById("error-dialog-message").innerHTML = respText;
			document.getElementById("wait-dialog").close();
			document.getElementById("error-dialog").showModal();
		}
	}).catch (function(error) {
    		console.log('Request failed', error);
		document.getElementById("error-dialog-message").innerHTML = "" + error;
		document.getElementById("wait-dialog").close();
		document.getElementById("error-dialog").showModal();
	});
}

// -----------------
// About dialog open
// -----------------
function showAboutDialog() {
  	document.getElementById("about-dialog").showModal();
}

// ---------------------------
// Handle and perform download
// ---------------------------
function downloadData() {
	try {
		// -----------------------
		// Check for existing data
		// -----------------------
		let value = getTableColVal("table-data", 1, 1);
		if (value == null) {
			let text = "No data to download.";
			document.getElementById("error-dialog-message").innerHTML = text;
			document.getElementById("error-dialog").showModal();
			return;
		}
		// -------------
		// Set file name
		// -------------
		let namePart = document.getElementById("combo-command").value;
		namePart = namePart.replace(/(\W+)/gi, '').trim();
		if (namePart.length == 0) {
			namePart = "command";
		}
		let fileName = "myminapp_" + namePart + ".txt"; //Avoid direct Excel-open
		// ----------------------------------
		// Set data to download as plain text
		// ----------------------------------
		let input = table2Csv("table-data");
		if (input == null) {
			let text = "No data to download.";
			document.getElementById("error-dialog-message").innerHTML = text;
			document.getElementById("error-dialog").showModal();
			return;
		}
		// -------------------------------------------------------------- 
		// Create a BLOB as binary representation of the plain-text input
		// --------------------------------------------------------------
		let blob = new Blob([input], {type:"text/plain;charset=utf-8"});
	 	// ----------------------------------------------------------------
		// Release a previous object URL from memory, then create a new one
		// ----------------------------------------------------------------
 		if (downloadUrl) {
 			URL.revokeObjectURL(downloadUrl);
		}
 		downloadUrl = URL.createObjectURL(blob);
		// ---------------------------------------------------
		// Create a download link and set the object URL to it
		// ---------------------------------------------------
		let a = document.createElement('a');
		a.href = "javascript:void(0)";
		a.download = fileName;
		document.body.appendChild(a)
		let download = document.querySelector("a[download]");
		download.setAttribute("href", downloadUrl);
		// -------------------------------------------------------
		// Perform download and remove the link from document body
		// -------------------------------------------------------
		download.click();
		document.body.removeChild(a)
	} catch (ex) {
		alert(ex.message);
	}
}

// -----------------------------------------
// Gets a specific column value from a table
// -----------------------------------------
function getTableColVal(tableId, rn, cn) {
	try {
		let table = document.getElementById(tableId);
		let rlen = table.rows.length;
		let clen = 0;
		let value = null;
		if (rlen >= rn) {
			clen = table.rows[rn-1].cells.length;
			if (clen >= cn) {
				value = table.rows[rn-1].cells[cn-1].innerText;
			}
		}
		return value;
	} catch (ex) {
		alert(ex.message);
		return null;
	}
}

// -------------------------------------------
// Converts table data to a CSV representation
// -------------------------------------------
function table2Csv(tableId) {
	try {
		let table = document.getElementById(tableId);
		let lines = [];
		let line = [];
		let line_sep = "\n";
		let col_sep = ";";
		for (let r=0, rlen=table.rows.length; r<rlen; r++) {
			line = [];
			for (let c=0, clen=table.rows[r].cells.length; c<clen; c++) {
				let value = table.rows[r].cells[c].innerText;
				if (c > 0) {
					line.push(col_sep);
				}
				value = value.replace(/(\r\n|\n|\r)/gm, "");
				line.push(value);
			}
			if (r > 0) {
				lines.push(line_sep);
			}
			lines.push(line.join(""));
		}
		return lines.join("");
	} catch (ex) {
		alert(ex.message);
		return null;
	}
}
