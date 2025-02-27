import numpy
from picamera2 import Picamera2
import threading
import StreamingOutput
import picamera2.encoders
import picamera2.outputs
from ProcessImage import ProcessImage
import time
from typing import Any

class ImageGenerator():
    ''''''
    def __init__(self, picam2: Picamera2, imageProcessor: ProcessImage):
        ''''''
        self.picam2 = picam2
        self.configureCam()

        self.imageProcessor = imageProcessor
        self.processImage = True

        self.processedImg = numpy.array([]) #image that has had processing applied to it, ready to be streamed
        self.currentImg = numpy.array([]) #last image that was captured from camera, processing gets applied to this image, then copied

        self.imageProcessThread = threading.Thread(target=self.CaptureBufferAndProcessImage)

    def configureCam(self):
        self.picam2.configure(self.picam2.create_video_configuration(main={"size": (640, 480), "format":"RGB888"}))
        self.picam2.set_controls({"ExposureTime": 1000000, "AnalogueGain": 10.0})
        self.picam2.post_callback = self.ModifyOutputImageOnCB


    def StartRecording(self, output: StreamingOutput):
        """
        Start recording to the output specified

        Args:
            output (StreamingOutput) The stream to be written to
        """
        self.picam2.start_recording(picamera2.encoders.MJPEGEncoder(), picamera2.outputs.FileOutput(output))
        #self.picam2.set_controls({"AnalogueGain": 10.0}) 
        self.imageProcessThread.start()


    def Stop(self):
        self.picam2.stop_recording()


    def ModifyOutputImageOnCB(self, request):
        """Copies over the output (stream) image with the processed image, if available. This method should subscribe to the picamera2 post/pre-callback event
        
        Args:
            request (picamera2 post/pre-callback request): Automatically supplied by picamera2's post_callback event - represents a single frame capture
        """
        with picamera2.MappedArray(request, "main") as mapArr:
            #potentially split image off here (write un modified image to separate stream)
            if (self.processImage and self.processedImg.size != 0):  
                if len(self.processedImg.shape) == 2:  # If it's a single-channel image (gray)
                    self.processedImg = numpy.stack([self.processedImg] * 3, axis=-1) #this converts it to a 3d array if its a 2d (grayscale)
                mapArr.array[:] = self.processedImg #replace the output image to be streamed with the processed image created in this class
            else:
                pass
    

    def CaptureBufferAndProcessImage(self): 
        """Captures individual image buffer and triggers image processor, writing over self.processedImg. The post_callback method should reference the output of this method"""
        lock = threading.Lock() #added because images sometimes being multiple-processed when processing takes too long
        while True: #always leaving thread running, stop event below with time.sleep is our pause mechanism
            while self.processImage:
                with lock:
                    self.currentImg = self.picam2.capture_array()
                    self.processedImg = self.imageProcessor.ProcessImage(self.currentImg)
            
            time.sleep(1) #delay to ease processing use while not running

    def ModifyCameraControls(self, setting: str, value: Any):
        if(setting == "AnalogueGain"):
            value = float(value)
        self.picam2.set_controls({setting: value}) 