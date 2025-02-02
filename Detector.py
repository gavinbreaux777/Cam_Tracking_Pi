import numpy
import picamera2
import threading
import StreamingOutput
import picamera2.encoders
import picamera2.outputs
from ProcessImage import ProcessImage
import time

from ImageGenerator import ImageGenerator

'''This class contains camera and image processing control - together they output detection results'''
class Detector():
    '''Init detector objects'''
    def __init__(self, picam2: picamera2.Picamera2):
        self._detected = False
        self._detectedLocation = [0,0]

        self.detected = property(self.GetDetected, self.SetDetected)
        self.detectedLocation = property(self.GetDetectedLocation, self.SetDetectedLocation)

        self.imgProc = ProcessImage(self.SetDetected, self.SetDetectedLocation)
        self.imgGen = ImageGenerator(picam2, self.imgProc)


    def GetDetected(self) -> bool:
        return self._detected

    def SetDetected(self, isDetected: bool):
        self._detected = isDetected
        print("Set detected")


    def GetDetectedLocation(self) -> tuple[int, int]:
        return self._detectedLocation

    def SetDetectedLocation(self, location: tuple[int, int]):
        self._detectedLocation = location
        print(f"Set detected location to {location}")


    def StartRecording(self, output: StreamingOutput):
        self.imgGen.StartRecording(output)