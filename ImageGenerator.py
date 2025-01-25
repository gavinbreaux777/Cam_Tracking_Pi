import numpy
import picamera2
import time
import cv2
import threading
import StreamingOutput
import picamera2.encoders
import picamera2.outputs


class ImageGenerator():
    def __init__(self, picam2: picamera2):
        ''''''
        self.picam2 = picam2
        self.picam2.configure(picam2.create_video_configuration(main={"size": (640, 480), "format":"RGB888"}))
        self.picam2.post_callback = self.ModifyOutputImageOnCB

        self.processedImg = numpy.array([]) #image that has had processing applied to it, ready to be streamed
        self.currentImg = numpy.array([]) #last image that was captured from camera, processing gets applied to this image, then copied

        self.imageProcessThread = threading.Thread(target=self.CaptureAndProcessImage)


    def StartRecording(self, output: StreamingOutput):
        """
        Start recording to the output specified

        Args:
            output (StreamingOutput) The stream to be written to
        """
        self.picam2.start_recording(picamera2.encoders.MJPEGEncoder(), picamera2.outputs.FileOutput(output))
        self.imageProcessThread.start()


    def Stop(self):
        self.picam2.stop_recording()


    def ModifyOutputImageOnCB(self, request):
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
            self.currentImg = self.picam2.capture_array()
            if (self.currentImg.size != 0):
                curTime = time.strftime("%Y-%m-%d %X")
                cv2.putText(self.currentImg, curTime, (0,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                self.processedImg = self.currentImg
        
