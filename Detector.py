import numpy
import picamera2
import threading
from StreamingOutput import StreamingOutput
import picamera2.encoders
import picamera2.outputs
from ProcessImage import ProcessImage
import time
from typing import Any

from ImageGenerator import ImageGenerator

'''This class contains camera and image processing control - together they output detection results'''
class Detector():
    '''Init detector objects'''
    def __init__(self, picam2: picamera2.Picamera2):
        self.detectedLocation = property(self._getDetectedLocation, self._setDetectedLocation) #Creating property this way so we can pass it as argument to ProcessImage class

        self._imgProcessor = ProcessImage(self._setDetectedLocation)
        self._imgGenerator = ImageGenerator(picam2, self._imgProcessor)

        self.output = StreamingOutput()

        #self.stopProcessingImgEvent = threading.Event()
        self._processImage = True


    @property
    def processImage(self):
        return self._processImage
    
    @processImage.setter
    def processImage(self, value: bool):
        self._processImage = value
        self._imgGenerator.processImage = value #This update starts/stops img processing in child class 



    def _getDetectedLocation(self) -> tuple[int, int]:
        return self._detectedLocation

    def _setDetectedLocation(self, location: tuple[int, int]):
        self._detectedLocation = location
        print(f"Set detected location to {location}")


    def StartRecording(self) -> None:
        self._imgGenerator.StartRecording(self.output)

    def StopRecording(self) -> None:
        self._imgGenerator.Stop()

    def ModifyImageProcessorSetting(self, settingName: str, settingValue: Any) -> None:
        if(settingName == "requiredObjectSize"):
            self._imgProcessor.requiredObjectSize = int(settingValue)