import picamera2

from FlaskServer import FlaskServer
from Detector import Detector
from MotorControl import MotorControl
from IOControl import IOControl

#Create class to handle camera and image processing
picam2 = picamera2.Picamera2()
detector = Detector(picam2)

#Create class to handle IO
ioControl = IOControl()

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

