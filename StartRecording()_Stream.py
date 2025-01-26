import picamera2

import threading

from FlaskServer import FlaskServer
from StreamingOutput import StreamingOutput

from ImageGenerator import ImageGenerator

from AimingControl import AimingControl
from Detector import Detector

#Create class to handle image generation (and modification)
picam2 = picamera2.Picamera2()
#imageGenerator = ImageGenerator(picam2)
detector = Detector(picam2)

try:
    #code start

    #Create class to control aiming steppers
    aimingControl = AimingControl()

    #Create stream output object to share between camera and server
    output = StreamingOutput()
    
    #Start the camera recording
    #imageGenerator.StartRecording(output)
    detector.StartRecording(output)

    #start Flask server with output from camera recording
    server = FlaskServer(output, detector.imgGen.processImgStopEvent, aimingControl)
    server.startServer()

finally:
    detector.imgGen.Stop()

