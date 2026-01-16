import config
from unittest.mock import create_autospec
from unittest.mock import MagicMock
from CameraInterface import CameraInterface
from IOInterface import IOInterface
from typing import cast

class ClassFactory():
    def __init__(self):
        pass

    @staticmethod
    def ReturnCamera():
        if(config.mockMode):
            camera : CameraInterface = MagicMock() #= create_autospec(CameraInterface, instance=True)
            return camera
        else:
            import picamera2.Picamera2
            return picamera2.Picamera2
    
    @staticmethod
    def ReturnIO():
        if(config.mockMode):
            io : IOInterface = MagicMock() #=create_autospec(IOInterface, instance=True)
            return io
        else:
            import pigpio
            return pigpio