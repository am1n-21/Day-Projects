////////////////////////////////////////////////////////////////////////////////

/* Document Elements */
const shiftTitleInputEl = document.getElementById("shift-title-input");
const timeDisplayEl = document.getElementById("time-display");
const startButtonEl = document.getElementById("shiftStart-btn");
const endButtonEl = document.getElementById("shiftEnd-btn");
const statsDisplayEl = document.getElementById("stats-display");
const buttonField = document.getElementById("button-field");

/* Local Script Variables */
let activeShift = false;
let tInterval;

////////////////////////////////////////////////////////////////////////////////

/**
 * Load Data: Function that will load data and update stored variables
 */
function loadData() {
    // Get state of shift
    const storageState = localStorage.getItem("shift")
    if (!storageState) {
        localStorage.setItem("shift", "");
    } else {
        activeShift = Boolean(storageState);
    }

    // Check if active shift going on
    if (activeShift) {
        update();
    }
    return;
}

/**
 * Start Button Event: Start shift when button is clicked
 */
function startClick() {
    // Set activeShift
    localStorage.setItem("shift", "true");

    // Store Name and Time
    localStorage.setItem("name", shiftTitleInputEl.value);
    localStorage.setItem("startTime", String(Date.now()));

    update();

    return;
};

/**
 * Update Function: Updates the HTML with new shift once started
 */
function update() {
    // Update to End Shift Button
    buttonField.innerHTML = 
    `<div id="button-field">
        <button class="shift-btn" id="shiftEnd-btn" onclick="endClick()">End Shift</button>
    </div>`

    // Update the name field
    shiftTitleInputEl.placeholder = "";

    // Update the name
    const shiftName = localStorage.getItem("name");
    statsDisplayEl.innerHTML = 
    `<div id="stats-display">
        Currently working the <em>${shiftName}<em> shift.
    </div>`

    // Update the time
    tInterval = setInterval(updateTime, 1000);
    return;
}

/**
 * Update Time Function: Calculates and Updates the Time of a shift
 */
function updateTime() {
    const startTime = localStorage.getItem("startTime");
    const shiftDur = Math.floor((Date.now() - startTime) / 1000);
    
    const hours = Math.floor(shiftDur / 3600);
    const minutes = Math.floor((shiftDur % 3600) / 60);
    const seconds = Math.floor(((Date.now() - startTime)% (1000 * 60)) / 1000);
    
    const displayTime = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`

    timeDisplayEl.textContent = displayTime;

    return;
}

/**
 * End Button Event: End shift when button is clicked
 */
function endClick() {
    // Set active shift
    localStorage.setItem("shift", "");

    clearInterval(tInterval);

    // Update to Start Shift Button
    buttonField.innerHTML = 
    `<div id="button-field">
        <button class="shift-btn" id="shiftStart-btn" onclick="startClick()">Start Shift</button>
    </div>`

    // Update the name field
    shiftTitleInputEl.placeholder = "Enter shift name";

    // Clear Time Display
    timeDisplayEl.textContent = "";

    // Calculate Total Time
    const currTotal = Date.now() - parseInt(localStorage.getItem("startTime"));
    const totalTime = localStorage.getItem("totalTime");

    if (!totalTime) {
        localStorage.setItem("totalTime", String(currTotal));
    } else {
        const finalTotal = currTotal + parseInt(totalTime);
        localStorage.setItem("totalTime", String(finalTotal));
    }

    // Update Total Time Display
    const total = localStorage.getItem("totalTime");
    const hours = ((total / 1000)/ 3600).toFixed(2);
    statsDisplayEl.textContent = `Total Shift Hours: ${hours}`;

    // Clear any remaining local store keys
    localStorage.removeItem("startTime");
    localStorage.removeItem("name");

    return;
};

////////////////////////////////////////////////////////////////////////////////

loadData();

////////////////////////////////////////////////////////////////////////////////
