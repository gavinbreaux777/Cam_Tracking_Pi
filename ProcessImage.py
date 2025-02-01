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
        self.baseImg = numpy.array([], dtype=numpy.uint8)

    def Old_ProcessImage(self, imgToProcess: numpy.ndarray[tuple[int,int,int]]) -> numpy.ndarray[tuple[int, int, int]]:
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
        
    def ProcessImage(self, imgToProcess: numpy.ndarray[tuple[int,int,int]]) -> numpy.ndarray[tuple[int, int, int]]:
        #convert image to grayscale and numpy uint8 array
        grayed = cv2.cvtColor(imgToProcess, cv2.COLOR_BGR2GRAY)
        numpy.uint8(grayed)

        #Ensure there is a base image
        if(self.baseImg.size == 0):
            self.baseImg = grayed
            return self.baseImg
        
        #Find difference between base image and current image
        delta = cv2.absdiff(grayed, self.baseImg)
        delta = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]

        #Find blobs of sufficient difference
        contours, _ = cv2.findContours(delta, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if cv2.contourArea(contour) < 100:
                continue
            (x,y,w,h) = cv2.boundingRect(contour)
            print(cv2.contourArea(contour))
            cv2.rectangle(grayed, (x, y), (x + w, y + h), (0,0,255),4)
        curTime = time.strftime("%Y-%m-%d %X")
        cv2.putText(grayed, curTime, (0,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        return grayed