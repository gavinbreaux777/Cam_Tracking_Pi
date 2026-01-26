from ClassFactory import ClassFactory
from AppConfig import AppConfig

from FlaskServer import FlaskServer
from Detector import Detector
from IOControl import IOControl

#load config values
config = AppConfig("config/")

#Create class to handle camera and image processing
picam2 = ClassFactory.ReturnCamera(config.cameraConfig)
detector = Detector(picam2)

#Create class to handle IO
io = ClassFactory.ReturnIO(config.ioConfig)
ioControl = IOControl(io)

#Create class to control all motors, aiming and projection
motorControl = ClassFactory.ReturnMotorControl(ioControl, config.motorConfig)

try:
    #code start
    
    #Start the camera recording
    detector.StartRecording()    

    #start Flask server with output from camera recording
    server = FlaskServer(detector, motorControl)

    detector.RegisterObserver(motorControl)
    detector.RegisterObserver(server)

    server.startServer()

finally:
    detector.StopRecording()

