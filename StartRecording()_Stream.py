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


#helper classes
class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = threading.Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

"""Handles stream and modifying image"""
class StreamModification():
    #when processing the current image to be sent, modifications sometimes not applied before image is sent - resulting in flickering graphics. Adding a buffered image fixed that
    processedImg = numpy.array([]) #image that has had processing applied to it, ready to be streamed
    currentImg = numpy.array([]) #last image that was captured from camera, processing gets applied to this image, then copied

    #Streaming cv2.imencode().tobytes() instead of output.frame results in couple second lag (no need to do that anyway)
    def gen_frames(self):
        """Stream method that returns processed jpeg images in html response format"""
        while True:
                if(self.processedImg.size != 0):
                    yield (b'--frame\r\n' 
                    b'Content-Type: image/jpeg\r\n\r\n' + output.frame + b'\r\n') 

    def post_callback_method(self, request):
        """Method called after each capture, before the image is sent out to streams. This method copies over the output (stream) frame with the processed image, if available"""
        with picamera2.MappedArray(request, "main") as mapArr:
            if (self.processedImg.size != 0): 
                mapArr.array[:] = self.processedImg #replace the output image to be streamed with the processed image created in this class
            else:
                print("processed image not available")

    def capture_request(self):
        """Method that captures individual image buffer and applies processing. The post_callback method should reference the output of this method"""
        while True:
            if(output.frame != None):
                self.currentImg = picam2.capture_array()
                if (self.currentImg.size != 0):
                    curTime = time.strftime("%Y-%m-%d %X")
                    cv2.putText(self.currentImg, curTime, (0,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                    self.processedImg = self.currentImg

"""Handles serving pages and image streams"""
class FlaskHandler():
    #init flask
    app = flask.Flask(__name__)
    #setup flask endpoints for http requests
    @app.route('/')
    def serve_page():
        return flask.render_template("Picamera2Page.html")

    @app.route('/stream')
    def send_html():
        return flask.Response(StreamModClass.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
    #start flask server
    app.run(host='0.0.0.0', port=5000, debug=False) #Script fails if debug=True (multiple instances of picamera2)



try:
    #code start
    app = flask.Flask(__name__)

    #create and configure camera object
    picam2 = picamera2.Picamera2()
    picam2.configure(picam2.create_video_configuration(main={"size": (640, 480), "format":"RGB888"}))
    (width, height) = picam2.stream_configuration("main")["size"]

    #setup stream and start recording
    output = StreamingOutput()
    StreamModClass = StreamModification()
    picam2.post_callback = StreamModClass.post_callback_method
    picam2.start_recording(picamera2.encoders.MJPEGEncoder(), picamera2.outputs.FileOutput(output))

    #run method that captures individual images and performs processing on them
    capture_request_thread = threading.Thread(target=StreamModClass.capture_request)
    capture_request_thread.start()

    server = FlaskHandler()

finally:
    picam2.stop_recording()

'''
#setup flask endpoints for http requests
@app.route('/')
def serve_page():
    return flask.render_template("Picamera2Page.html")

@app.route('/stream')
def send_html():
    return flask.Response(StreamModClass.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=False) #Script fails if debug=True (multiple instances of picamera2)
    finally:
        picam2.stop_recording()'''




