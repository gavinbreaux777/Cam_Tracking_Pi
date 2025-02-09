import time
import cv2
import numpy
from typing import Callable

class ProcessImage():
    '''Initialize image processing class.
    
        args:
            updateDetectLocationFunc: (Callable[bool]: function to call when motion is detected)
    '''
    def __init__(self, updateDetectedLocationFunc: Callable[[tuple[int,int]], None]):
        self._baseImg = numpy.array([], dtype=numpy.uint8)
        self.unprocessedImg = numpy.array([])
        self.processedImg = numpy.array([])
        self._detectedLocationReport = updateDetectedLocationFunc
        self.requiredObjectSize = 100

    def Old_ProcessImage(self, imgToProcess: numpy.ndarray[tuple[int,int,int]]) -> numpy.ndarray[tuple[int, int, int]]:
        '''Takes in image, performs processing, and returns the modified image. This function also reports motion detection status/location (runs "self.updateDetect...)'''
        if (imgToProcess.size != 0):
            curTime = time.strftime("%Y-%m-%d %X")
            cv2.putText(imgToProcess, curTime, (0,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            #put detection logic here. For more information transfer, consider making a single class like "detectionInfo" to return
            if(True):
                self._detectedLocationReport([1,2,3])
            else:
                self._detectedLocationReport = [0,0,0]
            return imgToProcess
        
    def ProcessImage(self, imgToProcess: numpy.ndarray[tuple[int,int,int]]) -> numpy.ndarray[tuple[int, int, int]]:
        #convert image to grayscale and numpy uint8 array
        grayed = cv2.cvtColor(imgToProcess, cv2.COLOR_BGR2GRAY)
        numpy.uint8(grayed)

        #Ensure there is a base image
        if(self._baseImg.size == 0):
            self._baseImg = grayed
            return self._baseImg
        
        #Find difference between base image and current image
        delta = cv2.absdiff(grayed, self._baseImg)
        delta = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]

        #Find blobs of sufficient difference
        contours, _ = cv2.findContours(delta, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if cv2.contourArea(contour) < self.requiredObjectSize:
                continue
            (x,y,w,h) = cv2.boundingRect(contour)
            print(cv2.contourArea(contour))
            cv2.rectangle(grayed, (x, y), (x + w, y + h), (0,0,255),4)

        #Append timestamp
        curTime = time.strftime("%Y-%m-%d %X")
        cv2.putText(grayed, curTime, (0,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        return grayed