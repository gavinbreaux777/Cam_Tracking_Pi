// UI Component functions (tabs, settings, actions)

let baseRenewal = null;

function openTab(evt, tabName) {
    // Remove the active class from all buttons
    document.querySelectorAll('.tab-buttons button').forEach((button) => {
        button.classList.remove('active');
    });

    // Show the current tab, hide others, and add an "active" class to the button that opened it
    document.querySelectorAll('.tabcontent').forEach(section => {
        const tabs = section.dataset.tabs.split(',').map(t => t.trim());
        if (tabs.includes(tabName)) {
            section.classList.add('active');
        } else {
            section.classList.remove('active');
        }
    });
    evt.currentTarget.classList.add('active');

    if(baseRenewal != null){
        console.log("clearing base renewal");
        clearInterval(baseRenewal);
        baseRenewal = null;
    }
    if(tabName == "side_by_side"){
        baseRenewal = setInterval(() => {
            document.getElementById("base-img").src = "/base-img?cache_buster=" + new Date().getTime();
        }, 1000);
    }
}

function actOnDetection(){
    const enableStr = !serverData.actOnDetection;
    fetch(`/actOnDetection/${enableStr}`, {
        method: 'GET'
    })
    .then(response => {
        if (response.status === 200){
            console.log("Enabled action on detection. Server response = " + response.body);
        }
        else{
            console.log("Failure to enable action on detection. Server response: " + response.status);
        }
    })
    .catch(error => {
        console.error(error)
    })
}

function changeImgProcSetting(settingName, settingValue){
    fetch(`/modImgProcSetting/${settingName}/${settingValue}`, {
        method: 'GET'
    })
    .then(response => {
        if (response.status == 200){
            console.log("Server is modifying setting. Response: " + response.text());
        }
        else{
            console.log("Error while requesting setting modification. Response: " + response.status);
        }
    })
    .catch(error => {
        console.error(error)
    })
}
