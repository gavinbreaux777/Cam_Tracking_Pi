import config
from unittest.mock import MagicMock
from CameraInterface import CameraInterface

class ClassFactory():
    def __init__(self):
        pass

    @staticmethod
    def ReturnCamera():
        if(config.mockMode):
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
    def ReturnIO():
        if(config.mockMode):
            return MagicMock()
        else:
            import pigpio
            return pigpio.pi()