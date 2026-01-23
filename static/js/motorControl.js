// Motor control functions (steppers and servos)

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

function stopMotors(){
    console.log("Stopping motors")
    fetch("/stopMotors",{
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
