import time
import cv2
import numpy
from typing import Callable
import skimage
import matplotlib.pyplot as plt

class ProcessImage():
    '''Initialize image processing class.
    
        args:
            updateDetectLocationFunc: (Callable[bool]: function to call when motion is detected)
    '''
    def __init__(self, updateDetectedLocationFunc: Callable[[tuple[int,int]], None]):
        self._baseImg = numpy.array([], dtype=numpy.uint8)
        self.unprocessedImg = numpy.array([])
        self.processedImg = numpy.array([])
        self._setDetectedLocation = updateDetectedLocationFunc
        self.requiredObjectSize = 2500
        
    def ProcessImage(self, imgToProcess: numpy.ndarray[tuple[int,int,int]]) -> numpy.ndarray[tuple[int, int, int]]:
        #convert image to grayscale and numpy uint8 array
        grayed = cv2.cvtColor(imgToProcess, cv2.COLOR_BGR2GRAY)
        numpy.uint8(grayed)

        #Ensure there is a base image
        if(self._baseImg.size == 0):
            if(grayed[0][0] != 0 and grayed[0][0] != 255): #Added this check because when image processing is stopped via Detector setting ProcessImage = False directly after motion found, the first captured image buffer from the cam is invalid (all 0's/255s)
                self._baseImg = grayed
            return self._baseImg
        
        #Find difference between base image and current image
        delta = cv2.absdiff(grayed, self._baseImg)
        delta = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]

        #Find blobs of sufficient difference
        contours, _ = cv2.findContours(delta, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        selected_contours = []
        #process each contour
        for contour in contours:
            if cv2.contourArea(contour) < self.requiredObjectSize:
                continue
            #Find bounding box for this contour and add to list of contours to reference later
            rotRect = cv2.minAreaRect(contour)
            rotBox = cv2.boxPoints(rotRect)
            rotBox = numpy.int0(rotBox)
            selected_contours.append(contour)

        #Combine all contours into one output contour and find center point
        if(len(selected_contours) > 0):
            all_selected_contours = numpy.concatenate(selected_contours, axis=0)
            rotRect = cv2.minAreaRect(all_selected_contours)
            rotBox = cv2.boxPoints(rotRect)
            rotBox = numpy.int0(rotBox)
            cv2.drawContours(grayed, [rotBox],0,(255,255,255),2)
            #find center of bounding box
            numPoints = rotBox.shape[0]
            xSum = numpy.sum(rotBox, axis=0)[0]
            ySum = numpy.sum(rotBox, axis=0)[1]
            xCenter = numpy.int0(xSum/numPoints)
            yCenter = numpy.int0(ySum/numPoints)
            cv2.circle(grayed, (xCenter, yCenter),5,(255,255,255),2)
            #report detected location
            self._setDetectedLocation([xCenter, yCenter])
            #after reporting detected location, clear base image so a new one will be created on next round of detection (after aim and fire sequence)
            self._baseImg = numpy.array([], dtype=numpy.uint8)
    

        # Append timestamp to image
        curTime = time.strftime("%Y-%m-%d %X")
        cv2.putText(grayed, curTime, (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        return delta