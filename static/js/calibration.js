// Calibration management class and functions

class Calibration {
    constructor(){
        this.items = {
            xClickRatio: null,
            yClickRatio: null,
            motorCalibrationStartX: null,
            motorCalibrationStartY: null,
            crosshairlength: 50
        }
    }

    saveLocation(clickEvent, imgWidth, imgHeight){
        //calculate and store x and y offset of click and current motor positions
        this.items.xClickRatio = (clickEvent.offsetX - (imgWidth/2)) / (imgWidth/2);
        this.items.yClickRatio = ((imgHeight/2) - clickEvent.offsetY) / (imgHeight/2);

        this.items.motorCalibrationStartX = serverData.xStepperPosition;
        this.items.motorCalibrationStartY = serverData.yStepperPosition;
        console.log("imgWidth = " + imgWidth + ", imgHeight = " + imgHeight);
        console.log("click X: " + clickEvent.offsetX + ", click Y: " + clickEvent.offsetY);
        console.log("streamImg width: " + document.getElementById("stream_img").width + ", height: " + document.getElementById("stream_img").height);

        //add save button, retain crosshair on clicked image and show new live image with crosshair centered
        const saveCalibrationBtn = document.createElement("button");
        saveCalibrationBtn.textContent = "Save Calibration";
        saveCalibrationBtn.onclick = () => {
            this.calculateAndPushCalibration()
        };
        
        saveCalibrationBtn.className = "save-clb-btn";

        const imgDivTwo = document.getElementById("img_div_two");
        imgDivTwo.innerHTML = "";

        const streamImg = document.getElementById("stream_img")

        const clickCanvas = document.createElement('canvas');        
        const ctx = clickCanvas.getContext('2d');
        clickCanvas.width = streamImg.width;
        clickCanvas.height = streamImg.height;
        ctx.drawImage(streamImg, 0, 0, clickCanvas.width, clickCanvas.height);
        
        ctx.strokeStyle = 'red';
        ctx.lineWidth = 2;
        this.items.crosshairlength = 50;
        
        //account for window resizing
        const scaleX = clickCanvas.width / imgWidth;
        const scaleY = clickCanvas.height / imgHeight;
        const crosshairX = clickEvent.offsetX * scaleX;        
        const crosshairY = clickEvent.offsetY * scaleY;
                
        drawCrosshair(ctx, crosshairX, crosshairY, this.items.crosshairlength, 'red', 2)

        const clickImage = new Image();
        clickImage.src = clickCanvas.toDataURL();

        clickImage.onload = () => {
            imgDivTwo.appendChild(clickImage);
            imgDivTwo.appendChild(saveCalibrationBtn);
        }
    
        //update calibration data display
        calibrationElements.xClickRatio_Element.innerHTML = Number(this.items.xClickRatio).toFixed(2);
        calibrationElements.yClickRatio_Element.innerHTML = Number(this.items.yClickRatio).toFixed(2);
        calibrationElements.xMotorStartPos_Element.innerHTML = Number(this.items.motorCalibrationStartX).toFixed(2);
        calibrationElements.yMotorStartPos_Element.innerHTML = Number(this.items.motorCalibrationStartY).toFixed(2);
        calibrationElements.workingCalibrationData_Element.classList.add("active");
    }

    //calculate deltas from new motor positions and initial positions, compute calibration factors and send to server
    calculateAndPushCalibration(){
        const motorXDelta = serverData.xStepperPosition - this.items.motorCalibrationStartX
        const motorYDelta = serverData.yStepperPosition - this.items.motorCalibrationStartY

        const xDegreesPerDetectDistanceRatio = motorXDelta / this.items.xClickRatio
        const yDegreesPerDetectDistanceRatio = motorYDelta / this.items.yClickRatio

        calibrationElements.xMotorDelta_Element.innerHTML = motorXDelta;
        calibrationElements.yMotorDelta_Element.innerHTML = motorYDelta;
        calibrationElements.PostSaveCalibrationData_Element.classList.add("active");
        
        sendMotorCalibrationFactors(xDegreesPerDetectDistanceRatio, yDegreesPerDetectDistanceRatio)
    }
}

const calibration = new Calibration();

function sendMotorCalibrationFactors(xCalibration, yCalibration){
    fetch(`/calibrateMotors/${xCalibration}/${yCalibration}`, {
        method: 'GET'
    })
    .then(response => {
        if (response.status == 200){
            console.log("Server is setting calibration factors. Response: " + response.text());
        }
        else{
            console.log("Error while requesting setting modification. Response: " + response.status);
        }
    })
    .catch(error => {
        console.error(error)
    })
}

function drawCrosshair(canvasContext, xCenter, yCenter, length, color, width){
    console.log("drawing crosshair at: " + xCenter + ", " + yCenter)
    canvasContext.strokeStyle = color;
    canvasContext.lineWidth = width;
    
    canvasContext.beginPath()
    canvasContext.moveTo(xCenter - length/2, yCenter)
    canvasContext.lineTo(xCenter + length/2, yCenter)
    canvasContext.stroke();

    canvasContext.beginPath()
    canvasContext.moveTo(xCenter, yCenter - length/2)
    canvasContext.lineTo(xCenter, yCenter + length/2)
    canvasContext.stroke();
    console.log("finished drawing crosshair")
}
