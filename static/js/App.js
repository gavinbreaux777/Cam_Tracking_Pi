// Global server data state
window.serverData = {
    xStepperPosition: 0,
    yStepperPosition: 0,
    servoPosition: 0,
    taughtOpen: null,
    taughtClosed: null,
    actOnDetection: 0,
    runMode: 0,
    xDegreesPerPercent: 0,
    yDegreesPerPercent: 0,
    streaming: false,
    tiltLowerLimit: null,
    tiltUpperLimit: null,
    aimMotorsHomed: null
}

// Cache DOM elements for quick access
const pageButtons = {
    imageModButton: document.getElementById("start_stop_img_mod"),
    streamButton: document.getElementById("start_stop_stream"),
    actOnDetectionButton: document.getElementById("toggle_act_on_detection")
}

const calibrationElements = {
    workingCalibrationData_Element: document.getElementById("working_calibration_data"),
    xDegreesPerPercent_Element: document.getElementById("x_degrees_per"),
    yDegreesPerPercent_Element: document.getElementById("y_degrees_per"),
    xClickRatio_Element: document.getElementById("xClickRatio"),
    yClickRatio_Element: document.getElementById("yClickRatio"),
    xMotorStartPos_Element: document.getElementById("motorCalibrationStartX"),
    yMotorStartPos_Element: document.getElementById("motorCalibrationStartY"),
    PostSaveCalibrationData_Element: document.getElementById("post_save_calibration_data"),
    xMotorDelta_Element: document.getElementById("motor_delta_x"),
    yMotorDelta_Element: document.getElementById("motor_delta_y")
}

const motorElements = {
    xStepperPos_Element: document.getElementById("x_stepper_pos"),
    yStepperPos_Element: document.getElementById("y_stepper_pos"),
    servoPos_Element: document.getElementById("servo-pos"),
    taughtOpen_Element: document.getElementById("taughtOpenVal"),
    taughtClosed_Element: document.getElementById("taughtClosedVal"),
    tiltLowerLimit_Element: document.getElementById("tilt-lower-limit"),
    tiltUpperLimit_Element: document.getElementById("tilt-upper-limit"),
    disabledWrappers: document.querySelectorAll(".mot-ctrl-item[data-item=extra] .btn-disabled-wrapper"),
    disabledLimitButtons: document.querySelectorAll(".mot-ctrl-item[data-item=extra] .btn-disabled-wrapper button")
}

// Initialize event sources on page load
document.addEventListener('DOMContentLoaded', initializeEventSources);

function initializeEventSources() {
    // Server state updates
    const dataEventSource = new EventSource('/dataEventSoruce');
    dataEventSource.onmessage = function(event) {
        serverData.runMode = JSON.parse(event.data).moddingImage;
        serverData.streaming = JSON.parse(event.data).streaming;
        serverData.actOnDetection = JSON.parse(event.data).actOnDetection;
        serverData.xDegreesPerPercent = JSON.parse(event.data).xDegreesPerPercent;
        serverData.yDegreesPerPercent = JSON.parse(event.data).yDegreesPerPercent;        
        updateStaticHTML();
    };
    dataEventSource.onerror = function() {
        console.error("EventSource failed.");
    };

    // Detection notifications
    const newDetectEventSource = new EventSource('/detectNotifySource');
    newDetectEventSource.onmessage = function(event) {
        displayDetectImg();
    }
    newDetectEventSource.onerror = function() {
        console.error("EventSource failed");
    }

    // Motor location updates
    const motorLocationSource = new EventSource('/motorLocation');
    motorLocationSource.onmessage = function(event){
        const eventData = JSON.parse(event.data);
        serverData.xStepperPosition = eventData.xPosition?.toFixed(2) ?? "--";
        serverData.yStepperPosition = eventData.yPosition?.toFixed(2) ?? "--";
        serverData.servoPosition = eventData.servoPosition?.toFixed(2) ?? "--";
        serverData.taughtOpen = eventData.taughtOpen?.toFixed(2) ?? "--";
        serverData.taughtClosed = eventData.taughtClosed?.toFixed(2) ?? "--";
        serverData.tiltLowerLimit = eventData.tiltLowerLimit?.toFixed(2) ?? "--";
        serverData.tiltUpperLimit = eventData.tiltUpperLimit?.toFixed(2) ?? "--";
        serverData.aimMotorsHomed = eventData.aimMotorsHomed ?? false;
        motorElements.xStepperPos_Element.textContent = serverData.xStepperPosition;
        motorElements.yStepperPos_Element.textContent = serverData.yStepperPosition;
        motorElements.servoPos_Element.textContent = serverData.servoPosition;
        motorElements.taughtOpen_Element.textContent = serverData.taughtOpen;
        motorElements.taughtClosed_Element.textContent = serverData.taughtClosed;
        motorElements.tiltLowerLimit_Element.textContent = serverData.tiltLowerLimit;
        motorElements.tiltUpperLimit_Element.textContent = serverData.tiltUpperLimit;
    }
}

function updateStaticHTML(){
    pageButtons.streamButton.classList.remove("on-btn", "off-btn");
    pageButtons.streamButton.classList.add(serverData.streaming ? "on-btn" : "off-btn");
    pageButtons.streamButton.innerHTML = serverData.streaming ? "Stop Stream" : "Start Stream";
    pageButtons.streamButton.onclick = serverData.streaming ? stopStream : startStream;

    pageButtons.imageModButton.classList.remove("on-btn", "off-btn");
    pageButtons.imageModButton.classList.add(serverData.runMode ? "on-btn" : "off-btn");
    pageButtons.imageModButton.innerHTML = serverData.runMode ? "Stop Detection" : "Run Detection";
    pageButtons.imageModButton.onclick = serverData.runMode ? stopImgMod : startImgMod;

    pageButtons.actOnDetectionButton.classList.remove("on-btn", "off-btn");
    pageButtons.actOnDetectionButton.classList.add(serverData.actOnDetection ? "on-btn" : "off-btn");
    pageButtons.actOnDetectionButton.innerHTML = serverData.actOnDetection ? "Disable Act on Detection" : "Enable Act on Detection";

    calibrationElements.xDegreesPerPercent_Element.innerHTML = Number(serverData.xDegreesPerPercent).toFixed(2);
    calibrationElements.yDegreesPerPercent_Element.innerHTML = Number(serverData.yDegreesPerPercent).toFixed(2);

    motorElements.disabledWrappers.forEach(btn => {
        if(serverData.aimMotorsHomed == true) {
            btn.classList.remove("btn-disabled-wrapper");
        }
        else{
            btn.classList.add("btn-disabled-wrapper");
        }
    })
    motorElements.disabledLimitButtons.forEach(btn => {
        if(serverData.aimMotorsHomed == true){
            btn.disabled = false;
        }
        else{
            btn.disabled = true;
        }
    })
}
