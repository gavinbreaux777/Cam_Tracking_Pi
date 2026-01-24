from ClassFactory import ClassFactory

from FlaskServer import FlaskServer
from Detector import Detector
from MotorControl import MotorControl
from IOControl import IOControl
from AppConfig import AppConfig
import os

#load config values
config = AppConfig.load_config("config/")
print(config.cameraConfig.mockMode)
os._exit(1)

#Create class to handle camera and image processing
picam2 = ClassFactory.ReturnCamera()
detector = Detector(picam2)

#Create class to handle IO
io = ClassFactory.ReturnIO()
ioControl = IOControl(io)

try:
    #code start
    
    #Start the camera recording
    detector.StartRecording()

    #Create class to control all motors, aiming and projection
    motorControl = MotorControl(ioControl)

    #start Flask server with output from camera recording
    server = FlaskServer(detector, motorControl)

    detector.RegisterObserver(motorControl)
    detector.RegisterObserver(server)

    server.startServer()

finally:
    detector.StopRecording()

