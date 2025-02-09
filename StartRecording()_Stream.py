import picamera2

from FlaskServer import FlaskServer

from StreamingOutput import StreamingOutput
from Detector import Detector
from MotorControl import MotorControl

#Create class to handle camera and image processing
picam2 = picamera2.Picamera2()
detector = Detector(picam2)

try:
    #code start

    #Create class to control all motors, aiming and projection
    motorControl = MotorControl()
    
    #Start the camera recording
    detector.StartRecording()#output)

    #start Flask server with output from camera recording
    server = FlaskServer(detector, motorControl)
    server.startServer()

finally:
    detector.StopRecording()

