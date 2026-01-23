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
        this.items.xClickRatio = (clickEvent.offsetX - (imgWidth/2)) / (imgWidth/2);
        this.items.yClickRatio = ((imgHeight/2) - clickEvent.offsetY) / (imgHeight/2);

        this.items.motorCalibrationStartX = serverData.xStepperPosition;
        this.items.motorCalibrationStartY = serverData.yStepperPosition;

        const saveCalibrationBtn = document.createElement("button");
        saveCalibrationBtn.textContent = "Save Calibration";
        saveCalibrationBtn.onclick = () => {
            this.calculateAndPushCalibration()
        };
        saveCalibrationBtn.style.margin = "20px auto";
        saveCalibrationBtn.style.display = "block";

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
        
        drawCrosshair(ctx, clickEvent.offsetX, clickEvent.offsetY, this.items.crosshairlength, 'red', 2)

        const clickImage = new Image();
        clickImage.src = clickCanvas.toDataURL();

        clickImage.onload = () => {
            imgDivTwo.appendChild(clickImage);
            imgDivTwo.appendChild(saveCalibrationBtn);
        }
    
        calibrationElements.xClickRatio_Element.innerHTML = Number(this.items.xClickRatio).toFixed(2);
        calibrationElements.yClickRatio_Element.innerHTML = Number(this.items.yClickRatio).toFixed(2);
        calibrationElements.xMotorStartPos_Element.innerHTML = Number(this.items.motorCalibrationStartX).toFixed(2);
        calibrationElements.yMotorStartPos_Element.innerHTML = Number(this.items.motorCalibrationStartY).toFixed(2);
        calibrationElements.workingCalibrationData_Element.classList.add("active");
    }

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
