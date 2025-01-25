#one method: Start thread that is constantly capturing images as arrays, modifying, and converting them to .jpg. 
#In the main server, loop and send the images being captured and manipulated in the other thread

#Another method: Use Picamera2's "StartRecording" method (which is faster than streaming individual .jpegs) and apply a "postCallback" method that puts graphics on the stream.
#The graphics being put in the "postCallback" method should be determined in another thread using the "CaptureRequest" method (Should it be "CaptureRequest" or somethinge else?)
#Like maybe capture buffer?

import threading

import picamera2

import picamera2.encoders
import picamera2.outputs

import threading

from FlaskServer import FlaskServer
from StreamingOutput import StreamingOutput

import ImageGenerator

#Create class to handle image generation (and modification)
picam2 = picamera2.Picamera2()
imageGenerator = ImageGenerator.ImageGenerator(picam2)

try:
    #code start

    #Create stream output object to share between camera and server
    output = StreamingOutput()
    imageGenerator.StartRecording(output)

    #start Flask server with output from camera recording
    server = FlaskServer(output)
    server.startServer()

finally:
    imageGenerator.Stop()

