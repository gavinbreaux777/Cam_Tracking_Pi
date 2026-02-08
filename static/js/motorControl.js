// Motor control functions (steppers, servos, and dc motors)
function startJog(direction, speed){
    console.log("Starting jog")
    fetch(`/motorControl/${direction}/${speed}`, {
        method: 'GET'
    })
    .then(response => {
        if (response.status == 200){
            console.log("Server moving motor. Response: " + response.body);
        }
        else{
            console.log("Error while requesting motor move. Response: " + response.status);
        }
    })
    .catch(error => {
        console.error(error)
    })
}

function stopAimMotors(){
    console.log("Stopping motors")
    fetch("/stopAimMotors",{
        method: 'GET'
    })
    .then(response => {
        if (response.status == 200){
            console.log("Server stopping motor. Response: " + response.body);
        }
        else{
            console.log("Error while requesting motor stop. Response: " + response.status);
        }
    })
    .catch(error => {
        console.error(error)
    })
}

function enableDisableMotor(motorStr, enable){
    fetch(`/enableDisableMotor/${motorStr}/${enable}`, {
        method: 'GET'
    })
    .then(response => {
        if (response.status == 200){
            console.log("Server is enabling/disabling motor. Response: " + response.text());
        }
        else{
            console.log("Error while requesting enable/disable of motor. Response: " + response.status);
        }
    })
    .catch(error => {
        console.error(error)
    })
}

function moveChamberServo(target){
    console.log("Moving servo");
    fetch(`/moveChamberServo/${target}`, {
        method: 'GET'
    })
    .then(response => {
        if (response.status == 200){
            console.log("Server moving servo. Response: " + response.body);
        }
        else{
            console.log("Error while requesting servo move. Response: " + response.status);
        }
    })
    .catch(error => {
        console.error(error)
    })
}

function openChamberServo(target){
    console.log("Opening servo");
    fetch(`/openChamberServo`, {
        method: 'GET'
    })
    .then(response => {
        if (response.status == 200){
            console.log("Server moving servo. Response: " + response.body);
        }
        else{
            console.log("Error while requesting servo move. Response: " + response.status);
        }
    })
    .catch(error => {
        console.error(error)
    })
}

function closeChamberServo(target){
    console.log("Closing servo");
    fetch(`/closeChamberServo`, {
        method: 'GET'
    })
    .then(response => {
        if (response.status == 200){
            console.log("Server moving servo. Response: " + response.body);
        }
        else{
            console.log("Error while requesting servo move. Response: " + response.status);
        }
    })
    .catch(error => {
        console.error(error)
    })
}

function teachServo(state){
    console.log("Teaching servo: " + state);
    fetch(`/teachServo/${state}`, { method: 'GET' })
    .then(response => {
        if (response.status == 200){
            console.log("Server taught servo. Response: " + response.text());
        }
        else{
            console.log("Error teaching servo. Response: " + response.status);
        }
    })
    .catch(error => {
        console.error(error)
    })
}

function enableDisableDCMotors(enable){
    fetch(`/enableDisableDCMotor/${enable}`, {
        method: 'GET'
    })
    .then(response => {
        if (response.status == 200){
            console.log("Server is enabling/disabling DC motors. Response: " + response.text());
        }
        else{
            console.log("Error while requesting enable/disable of DC motors. Response: " + response.status);
        }
    })
    .catch(error => {
        console.error(error)
    })
}

let spoolID = null;
function spoolDCMotors(){
    fetch(`/spoolDCMotors`, {
        method: 'GET'
    })
    .then(response => {
        if (response.status == 200){
            console.log("Server is spooling DC motors. Response: " + response.text());
        }
        else{
            console.log("Error while requesting spooling of DC motors. Response: " + response.status);
        }
    })
    .catch(error => {
        console.error(error)
    })
}

function stopSpoolingDCMotors(){
    fetch(`/stopDCMotors`, {
        method: 'GET'
    })
    .then(response => {
        if (response.status == 200){
            console.log("Server is stopping DC motors. Response: " + response.text());
        }
        else{
            console.log("Error while requesting stop of DC motors. Response: " + response.status);
        }
    })
    .catch(error => {
        console.error(error)
    })
}

document.addEventListener('DOMContentLoaded', initializeMotorControlButtons);
const motorControlButtons = document.querySelectorAll(".mot-ctrl-item[data-action]");
function initializeMotorControlButtons(){
    motorControlButtons.forEach(button => {
        button.addEventListener("click", () => {
            const action = button.getAttribute("data-action");            
            console.log("Motor control button clicked with action: " + action);
            switch(action){            
                case "set-upper":
                    RecordUpperTiltLimit(window.serverData.yStepperPosition);   
                    break;         
                case "set-lower":
                    RecordLowerTiltLimit(window.serverData.yStepperPosition);
                    break;
                case "reset-limits":
                    ResetTiltLimits();
                    break;
                case "set-home":
                    SetAimMotorsHome()
                    break;
                case "move-home":
                    MoveAimMotorsHome()
                    break;
                case "toggle-extra":
                    ToggleExtraStepperControl(button)
                    break;
                default:
                    console.log("Unknown motor control action: " + action);
            }})
    })
}

function RecordUpperTiltLimit(limit){
    fetch(`/setTiltLimit/upper/${limit}`, {
        method: 'GET'
    })
    .then(response => {
        if(response.status == 200){
            console.log("Upper limit set successfully.");
        }
    })
    .catch(error => {
        console.error(error)
    })
}

function RecordLowerTiltLimit(limit){
    fetch(`/setTiltLimit/lower/${limit}`, {
        method: 'GET'
    })
    .then(response => {
        if(response.status == 200){
            console.log("Lower limit set successfully.");
        }
    })
    .catch(error => {
        console.error(error)
    })
}

function SetAimMotorsHome(){
    fetch('/setAimMotorsHome', {
        method: 'GET'
    })
    .then(response => {
        if(response.status == 200){
            console.log("Aim motors home set successfully.");
            const limitButtons = [...motorControlButtons].filter(
            btn => btn.dataset.action === 'set-upper' || btn.dataset.action === 'set-lower' || btn.dataset.action == "move-home"
            );
            limitButtons.forEach(btn => btn.removeAttribute("disabled"));
        }
    })
    .catch(error => {
        console.error(error)
    })
}

function MoveAimMotorsHome(){
    fetch('/moveAimMotorsHome', {
        method: 'GET'
    })
    .then(response => {
        if(response.status == 200){
            console.log("Aim motors moved to home position.");
        }
    })
    .catch(error => {
        console.error(error)
    })
}

function ResetTiltLimits(){
    RecordLowerTiltLimit(-999);
    RecordUpperTiltLimit(999);    
}

function ToggleExtraStepperControl(toggleButton){
    extraRow = document.querySelector(".mot-ctrl-item[data-item=extra]");
    //get computed style here because display=none set by css shows as <empty string> in js
    if(getComputedStyle(extraRow).display == "none") {
        extraRow.style.display = "flex";
         toggleButton.textContent = "Show Less";
    }
    else{
        extraRow.style.display = "none";
        toggleButton.textContent = "Show More";
    }
}

