#one method: Start thread that is constantly capturing images as arrays, modifying, and converting them to .jpg. 
#In the main server, loop and send the images being captured and manipulated in the other thread

#Another method: Use Picamera2's "StartRecording" method (which is faster than streaming individual .jpegs) and apply a "postCallback" method that puts graphics on the stream.
#The graphics being put in the "postCallback" method should be determined in another thread using the "CaptureRequest" method (Should it be "CaptureRequest" or somethinge else?)
#Like maybe capture buffer?

import io
import threading
import time

import picamera2

import flask
import picamera2.encoders
import picamera2.outputs

import numpy
import cv2

import threading

from types import FunctionType

#helper classes
class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = threading.Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class StreamModification():
    """Handles modifying raw image and overwriting output image before streaming it"""
    def __init__(self):
        '''
        Initialize stream modification class
        '''
        #when processing the current image to be sent, modifications sometimes not applied before image is sent - resulting in flickering graphics. Adding a buffered image fixed that
        self.processedImg = numpy.array([]) #image that has had processing applied to it, ready to be streamed
        self.currentImg = numpy.array([]) #last image that was captured from camera, processing gets applied to this image, then copied

    def ModifyOutputImage(self, request):
        """Copies over the output (stream) image with the processed image, if available. This method should subscribe to the picamera2 post/pre-callback event
        
        Args:
            request (picamera2 post/pre-callback request): Automatically supplied by picamera2's post_callback event - represents a single frame capture
        """
        with picamera2.MappedArray(request, "main") as mapArr:
            if (self.processedImg.size != 0): 
                mapArr.array[:] = self.processedImg #replace the output image to be streamed with the processed image created in this class
            else:
                print("processed image not available")

    def CaptureAndProcessImage(self):
        """Captures individual image buffer and applies processing. The post_callback method should reference the output of this method"""
        while True:
            self.CaptureImage()
            self.ProcessImage()

    def CaptureImage(self):
            self.currentImg = picam2.capture_array()

    def ProcessImage(self):
        if (self.currentImg.size != 0):
                curTime = time.strftime("%Y-%m-%d %X")
                cv2.putText(self.currentImg, curTime, (0,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                self.processedImg = self.currentImg


class FlaskServer:    
    '''Handles serving pages and image streams via Flask'''
    def __init__(self, streamImageSource: StreamingOutput):
        '''
        Initialize FlaskServer
        
        Args:
            streamImageSource (StreamingOutput): The source of images to be streamed (this image will be streamed each time it is updated)
        '''
        self.app = flask.Flask(__name__)
        self.imageSource = streamImageSource
        self.stopStreamEvent = threading.Event()
        self._define_routes()

    def _define_routes(self):
        """Define Flask routes using add_url_rule."""
        self.app.add_url_rule('/', 'serve_page', self.serve_page)
        self.app.add_url_rule('/stream', 'start_stream', self.start_stream)
        self.app.add_url_rule('/stopStream', 'stop_stream', self.stopStream())


    #Endpoint methods for flask endpoints
    def serve_page(self):
        return flask.render_template("Picamera2Page.html")
    
    def start_stream(self):
        self.stopStreamEvent.clear()
        return flask.Response(self.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
    def stopStream(self):
        """Stop streaming frames"""
        print("setting stop event")
        self.stopStreamEvent.set()

    #Helper methods to endpoint methods
    def gen_frames(self):
        """Stream method that returns processed jpeg images in html response format"""
        while not self.stopStreamEvent.is_set():
            with self.imageSource.condition:
                self.imageSource.condition.wait() #Waits for the imageSource to be renewed
                yield (b'--frame\r\n' 
                b'Content-Type: image/jpeg\r\n\r\n' + self.imageSource.frame + b'\r\n') 

    #App control methods
    def startServer(self):
        """Run the Flask server."""
        #access page via 10.0.0.40:5000, localhost:5000, 127.0.0.1:5000
        self.app.run(host='0.0.0.0', port=5000, debug=False)



class CameraHandler():
    def __init__(self, picam2: picamera2.Picamera2, post_callback_func: FunctionType):
        self.picam2 = picam2
        self.picam2.configure(picam2.create_video_configuration(main={"size": (640, 480), "format":"RGB888"}))
        picam2.post_callback = post_callback_func
        self.output = StreamingOutput
    
    def StartRecording(self, output: StreamingOutput):
        """
        Start recording to the output specified

        Args:
            output (StreamingOutput) The stream to be written to
        """
        self.picam2.start_recording(picamera2.encoders.MJPEGEncoder(), picamera2.outputs.FileOutput(output))

    def Stop(self):
        self.picam2.stop_recording()
        



try:
    #code start

    #create image modification class to process images
    StreamModClass = StreamModification()

    #create camera class to handle camera control
    picam2 = picamera2.Picamera2()
    output = StreamingOutput()
    cameraHandler = CameraHandler(picam2, StreamModClass.ModifyOutputImage)
    cameraHandler.StartRecording(output)

    #run method that captures individual images and performs processing on them
    imageProcess_thread = threading.Thread(target=StreamModClass.CaptureAndProcessImage)
    imageProcess_thread.start()

    #start Flask server
    server = FlaskServer(output)
    server.startServer()

finally:
    cameraHandler.Stop()

