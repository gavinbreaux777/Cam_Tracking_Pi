import time
import cv2
import numpy
from types import FunctionType

class ProcessImage():
    ''''''
    def __init__(self, updateDetectStatusFunc: FunctionType, updateDetectedLocationFunc: FunctionType):
        self.unprocessedImg = numpy.array([])
        self.processedImg = numpy.array([])
        self.detectedReport = updateDetectStatusFunc
        self.detectedLocationReport = updateDetectedLocationFunc

    def ProcessImage(self, imgToProcess: numpy.ndarray[tuple[int,int,int]]) -> numpy.ndarray[tuple[int, int, int]]:
        '''Takes in image, performs processing, and returns the modified image. This function also reports motion detection status/location (runs "self.updateDetect...)'''
        if (imgToProcess.size != 0):
            curTime = time.strftime("%Y-%m-%d %X")
            cv2.putText(imgToProcess, curTime, (0,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            #put detection logic here. For more information transfer, consider making a single class like "detectionInfo" to return
            if(True):
                self.detectedReport(True)
                self.detectedLocationReport([1,2,3])
            else:
                self.detectedReport = False
                self.detectedLocationReport = [0,0,0]
            return imgToProcess