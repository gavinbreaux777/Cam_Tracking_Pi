from AppConfig import *
from unittest.mock import MagicMock
from CameraInterface import CameraInterface

class ClassFactory():
    def __init__(self):
        pass

    @staticmethod
    def ReturnCamera(config: CameraConfig):
        if(config.mock):
            return MagicMock()
        else:
            import picamera2
            picamFromLib = picamera2
            cameraInterfacePicam = CameraInterface()
            cameraInterfacePicam.Picamera2 = picamFromLib.Picamera2()
            cameraInterfacePicam.encoders = picamera2.encoders
            cameraInterfacePicam.outputs = picamera2.outputs
            cameraInterfacePicam.Picamera2.MappedArray = picamFromLib.MappedArray
            return cameraInterfacePicam

    @staticmethod
    def ReturnIO(config: IOConfig):
        if(config.mock):
            return MagicMock()
        else:
            import pigpio
            return pigpio.pi()
        
    @staticmethod
    def ReturnMotorControl(ioControl, motorConfig: MotorConfig):
        from MotorControl import MotorControl
        if(motorConfig.aimMotors.panMotor.mock or
           motorConfig.aimMotors.tiltMotor.mock or 
           motorConfig.firingMotor.mock or 
           motorConfig.chamberServo.mock):
            raise Exception("Individual motor mocking not supported yet - use IO mocking instead to mock all motors")
        else:
            return MotorControl(ioControl, motorConfig)