// Camera and streaming control functions

function stopStream(){
    fetch('/stopStream', {
        method: 'GET'
    })
    .then(response => {
        if (response.status === 200){
            console.log("Stream stopped. Server response = " + response.body);
        }
        else{
            console.log("Failure to stop stream. Server response: " + response.status);
        }
    })
    .catch(error => {
        console.error(error)
    })
}

function startStream(){
    const btn = document.getElementById("start_stop_stream")
    const stream = document.getElementById("stream_img")
    fetch('/stream',{
        method: 'GET'
    })
    .then(response => {
        if (response.status === 200){
            console.log("Stream started. Server response = " + response.body);
        }
        else{
            console.log("Server failed to start stream. Server response: " + response.status)
        }
    })
    .then(data => {
        stream.src = "/stream"
    })
    .catch(error => {
        console.error(error)
    })
}

function stopImgMod(){
    fetch('/stopImgMod', {
        method: 'GET'
    })
    .then(response => {
        if (response.status === 200){
            console.log("Image mod stopped. Server response = " + response.body);
        }
        else{
            console.log("Failure to stop image mod. Server response: " + response.status);
        }
    })
    .catch(error => {
        console.error(error)
    })
}

function startImgMod(){
    fetch('/startImgMod', {
        method: 'GET'
    })
    .then(response => {
        if (response.status === 200){
            console.log("Image mod started. Server response = " + response.body);
        }
        else{
            console.log("Failure to start image mod. Server response: " + response.status);
        }
    })
    .catch(error => {
        console.error(error)
    })
}

function displayDetectImg(){
    const detectImg = document.getElementById("detect_img");
    detectImg.src = "/detect-img?cache_buster=" + new Date().getTime();
    detectImg.style.display = "block";
}

function hideDetectImg(){
    const detectImg = document.getElementById("detect_img");
    detectImg.style.display = "none";
}

document.getElementById("detect_img").onclick = hideDetectImg;

function forceDetection(clickEvent, imgWidth, imgHeight){
    const xClickRatio = (clickEvent.offsetX - (imgWidth/2)) / (imgWidth/2);
    const yClickRatio = ((imgHeight/2) - clickEvent.offsetY) / (imgHeight/2);
    console.log("location = " + xClickRatio + ", " + yClickRatio);
    fetch(`/forceDetection/${xClickRatio}/${yClickRatio}`, {
        method: 'GET'
    })
    .then(response => {
        if (response.status == 200){
            console.log("Server is responding to detection. Response: " + response.text());
        }
        else{
            console.log("Error while requesting forcing detection. Response: " + response.status);
        }
    })
    .catch(error => {
        console.error(error)
    })
}

function toggleDelta(clicked){
    fetch(`/toggleDelta/${clicked}`, {
        method: 'GET'
    })
    .then(response => {
        if (response.status == 200){
            console.log("Server is changing shown image. Response: " + response.text());
        }
        else{
            console.log("Error while requesting different image. Response: " + response.status);
        }
    })
    .catch(error => {
        console.error(error)
    })
}

function toggleContours(clicked){
    fetch(`/toggleContours/${clicked}`, {
        method: 'GET'
    })
    .then(response => {
        if (response.status == 200){
            console.log("Server is changing shown image. Response: " + response.text());
        }
        else{
            console.log("Error while requesting different image. Response: " + response.status);
        }
    })
    .catch(error => {
        console.error(error)
    })
}

function changeCamSetting(settingName, settingValue){
    fetch(`/modCamSetting/${settingName}/${settingValue}`, {
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
