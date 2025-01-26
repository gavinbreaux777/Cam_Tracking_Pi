import picamera2
import picamera2.encoders
import picamera2.outputs

import threading

from FlaskServer import FlaskServer
from StreamingOutput import StreamingOutput

import ImageGenerator

from AimingControl import AimingControl

#Create class to handle image generation (and modification)
picam2 = picamera2.Picamera2()
imageGenerator = ImageGenerator.ImageGenerator(picam2)

try:
    #code start

    #Create class to control aiming steppers
    aimingControl = AimingControl()

    #Create stream output object to share between camera and server
    output = StreamingOutput()
    imageGenerator.StartRecording(output)

    #start Flask server with output from camera recording
    server = FlaskServer(output)
    server.startServer()

finally:
    imageGenerator.Stop()

