const settingsElements = {
    panTiltSpeed_Input: document.getElementById("pan-tilt-speed")
}

settingsElements.panTiltSpeed_Input.addEventListener('change', e => setPanTiltSpeed(e.target.value));

function setPanTiltSpeed(speed){
    fetch(`/setPanTiltSpeed/${speed}`, {
        method: 'GET'
    })
    .then(response => {
        if(response.status == 200){
            console.log("Pan/Tilt speed set.");
        }
    })
    .catch(error => {
        console.error(error)
    })
}