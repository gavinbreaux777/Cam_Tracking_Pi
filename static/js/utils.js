// Utility functions

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
