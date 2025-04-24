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
        self.detectImg = numpy.array([], dtype=numpy.uint8)
        self._setDetectedLocation = updateDetectedLocationFunc
        self.requiredObjectSize = 10000
        self._baseRenewImageDelay = 0
        self._consecutiveDetections = 0
        self.showDelta = False #Return binary image representing pixels different than base past the threshold
        self.showContours = False #Draw difference contours on selected image
        
    def ProcessImage(self, imgToProcess: numpy.ndarray[tuple[int,int,int]]) -> numpy.ndarray[tuple[int, int, int]]:
        #convert image to grayscale and numpy uint8 array
        grayed = cv2.cvtColor(imgToProcess, cv2.COLOR_BGR2GRAY)
        numpy.uint8(grayed)

        #Ensure there is a base image
        if(self._baseImg.size == 0):
            self._baseRenewImageDelay += 1 
            if(self._baseRenewImageDelay > 2): #Added this check because when image processing is stopped via Detector setting ProcessImage = False directly after motion found, the first few captured image buffer from the cam is invalid (all 0's/255s) or it is old image with processing overlay still on it
                self._baseImg = grayed
                self._baseRenewImageDelay = 0
            return self._baseImg
        
        #Find difference between base image and current image
        delta = cv2.absdiff(grayed, self._baseImg)
        delta = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]

        #Select which image to draw on and return to stream
        if(self.showDelta == True):
            selectedImage = delta
        else:
            selectedImage = grayed

        #Find blobs of sufficient difference
        contours, _ = cv2.findContours(delta, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if(self.showContours == True):
                cv2.drawContours(selectedImage, contours,0,(255,255,255),2)
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
            #Find bounding box
            all_selected_contours = numpy.concatenate(selected_contours, axis=0)
            rotRect = cv2.minAreaRect(all_selected_contours)
            rotBox = cv2.boxPoints(rotRect)
            rotBox = numpy.int0(rotBox)
            #Draw bounding box
            cv2.drawContours(selectedImage, [rotBox],0,(255,255,255),2)
            #Conditionally draw contours if chosen
            if(self.showContours == True):
                cv2.drawContours(selectedImage, selected_contours,0,(255,255,255),2)
            #find center of bounding box
            numPoints = rotBox.shape[0]
            xSum = numpy.sum(rotBox, axis=0)[0]
            ySum = numpy.sum(rotBox, axis=0)[1]
            xCenter = numpy.int0(xSum/numPoints)
            yCenter = numpy.int0(ySum/numPoints)
            cv2.circle(selectedImage, (xCenter, yCenter),5,(255,255,255),2)
            
            #Only report motion found if not at edge of image
            if(xCenter > 640 * 0.1 and xCenter < 640 * .9) and (yCenter > 480 * 0.1 and yCenter < 480 * 0.9):
                #Wait for motion to be found several times in a row
                self._consecutiveDetections += 1
                if (self._consecutiveDetections > 10):
                    self._consecutiveDetections = 0
                    #report detected location
                    #Y axis is flipped from what we want (here, positive Y is bottom edge). Flip it to have positive y = top of image
                    print("shape = " + str(grayed.shape[0]))
                    print("original y = " + str(yCenter))
                    yCenter = abs(grayed.shape[0] - yCenter)
                    print("new y = " + str(yCenter))
                    self._setDetectedLocation([xCenter, yCenter])
                    print(f"Detected center at {xCenter, yCenter}")
                    #after reporting detected location, clear base image so a new one will be created on next round of detection (after aim and fire sequence)
                    self._baseImg = numpy.array([], dtype=numpy.uint8)
                    self.detectImg = selectedImage
        else: 
            self._consecutiveDetections = 0 #motion not detected, reset detection count
    

        # Append timestamp to image
        curTime = time.strftime("%Y-%m-%d %X")
        cv2.putText(selectedImage, curTime, (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        return selectedImage