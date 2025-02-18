import numpy
import picamera2
import threading
from StreamingOutput import StreamingOutput
import picamera2.encoders
import picamera2.outputs
from ProcessImage import ProcessImage
from Observer import DetectionObserver
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

        self._processImage = True

        self.observers: list[DetectionObserver] = []



    @property
    def processImage(self):
        return self._processImage
    
    @processImage.setter
    def processImage(self, value: bool):
        self._processImage = value
        self._imgGenerator.processImage = value #This update starts/stops img processing in child class 


    def _getDetectedLocation(self) -> tuple[int, int]:
        '''Getter for self.detectedLocation'''
        return self._detectedLocation

    def _setDetectedLocation(self, location: tuple[int, int]):
        '''Setter for self.detectedLocation. Notifies observers and stops image processing'''
        self._detectedLocation = location
        self._notifyObservers()
        #tell image process class to change behavior here (ie, stop detecting etc.) (or could have image process class do it directly)
        #then have motor control class inform detector here that firing sequence has completed
        self.processImage = False #when this is called from here, the first image captured in process image once this is reset is all 0's and 255's. Added handling for it to ProcessImage

    def _notifyObservers(self):
        '''Notify registered observers that motion has been detected with location. Once all observers have acknowledged the notification, restart image processing'''
        _completedObserverCount = 0

        def _observerDone(observer):
            nonlocal _completedObserverCount
            _completedObserverCount += 1
            print(f"observer #{_completedObserverCount} has completed its task")
            if(_completedObserverCount == len(self.observers)):
                print("All observers finished")
                self.processImage = True

        for observer in self.observers:
             threading.Thread(target=observer.OnMotionFound, args=(self._getDetectedLocation(), _observerDone,)).start() 

    def RegisterObserver(self, newObserver: DetectionObserver):
        '''Register new observer to be notified when motion has been detected'''
        self.observers.append(newObserver)

    def StartRecording(self) -> None:
        self._imgGenerator.StartRecording(self.output)

    def StopRecording(self) -> None:
        self._imgGenerator.Stop()

    def ModifyImageProcessorSetting(self, settingName: str, settingValue: Any) -> None:
        if(settingName == "requiredObjectSize"):
            self._imgProcessor.requiredObjectSize = int(settingValue)