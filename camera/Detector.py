from typing import Any
import threading
from .CameraInterface import CameraInterface
from .StreamingOutput import StreamingOutput
from .ProcessImage import ProcessImage
from helpers.Observer import DetectionObserver
from .ImageGenerator import ImageGenerator

'''This class contains camera and image processing control - together they output detection results'''
class Detector():
    '''Init detector objects'''
    def __init__(self, picam2: CameraInterface):
        self.detectedLocation = property(self._getDetectedLocation, self._setDetectedLocation) #Creating property this way so we can pass it as argument to ProcessImage class

        self._imgProcessor = ProcessImage(self._setDetectedLocation)
        self._imgGenerator = ImageGenerator(picam2, self._imgProcessor)

        self.output = StreamingOutput()

        self.observers: list[DetectionObserver] = []



    @property
    def processImage(self):
        return self._imgGenerator.processImage
    
    @processImage.setter
    def processImage(self, value: bool):
        self._imgGenerator.processImage = value #This update starts/stops img processing in child class 

    @property
    def showDelta(self):
        return self._imgProcessor.showDelta

    @showDelta.setter
    def showDelta(self, value: bool):
        self._imgProcessor.showDelta = value

    @property
    def showContours(self):
        return self._imgProcessor.showContours
    
    @showContours.setter
    def showContours(self, value: bool):
        self._imgProcessor.showContours = value


    def _getDetectedLocation(self) -> tuple[int, int]:
        '''Getter for self.detectedLocation'''
        return self._detectedLocation

    def _setDetectedLocation(self, location: tuple[int, int]):
        '''Setter for self.detectedLocation. Notifies observers and stops image processing'''
        newX = -location[0] #x motor is flipped from our x axis, reverse it
        newY = -location[1] #y motor is flipped from our y axis, reverse it
        self._detectedLocation = [newX, newY]
        print("Setting detected location at "  + str(self._detectedLocation))
        self._notifyObservers()
        print("Observers notified")
        #tell image process class to change behavior here (ie, stop detecting etc.) (or could have image process class do it directly)
        #then have motor control class inform detector here that firing sequence has completed
        self.processImage = False 

    def setDetectedRatio(self, xRatio: float, yRatio: float):
        '''Pushes x and y offset-from-center ratios to "setDetectedLocation" to create manual detection
            Args:
                xRatio (float): percentage of detection point away from center. 1 = far right edge, -1 = far left edge
                yRatio (float): percentage of detection point away from center. 1 = top edge, -1 = bottom edge
        "'''
        self._setDetectedLocation((xRatio, yRatio))

    def _notifyObservers(self):
        '''Notify registered observers that motion has been detected with location. Once all observers have acknowledged the notification, restart image processing'''
        _completedObserverCount = 0

        def _observerDone(observer):
            nonlocal _completedObserverCount
            _completedObserverCount += 1
            if(_completedObserverCount == len(self.observers)):
                pass
                #self.processImage = True #auto restart image processing

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

    def ModifyCameraSetting(self, settingName: str, settingValue: Any) -> None:
        self._imgGenerator.ModifyCameraControls(settingName, settingValue)