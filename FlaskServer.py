import flask
from flask import json
import threading
from motors.MotorControl import MotorControl
from camera.Detector import Detector
from helpers.Observer import DetectionObserver
import time
from typing import Callable
from PIL import Image
from io import BytesIO
from motors.MotorEnums import MotorEnum
from config.AppConfig import AppConfig
from routes.motors import create_motors_blueprint
from routes.imageProcessing import create_imageProcessing_blueprint

class FlaskServer(DetectionObserver):    
    '''Handles serving pages and image streams via Flask'''
    def __init__(self, detector: Detector, motorControl: MotorControl, config: AppConfig):
        '''
        Initialize FlaskServer
        
        Args:
            streamImageSource (StreamingOutput): The source of images to be streamed (this image will be streamed each time it is updated)
            stopProcessingImagesEvent (threading.Event): Event to raise when client requests stop of image processing
            motorControl (MotorControl): Class to pass client motor-control commands to
        '''
        self.app = flask.Flask(__name__)
        self._detector = detector
        self._imageSource = self._detector.output
        self._baseImage = self._detector._imgProcessor._baseImg        
        self._motorControl = motorControl
        self._motorConfig = config.motorConfig
        self._systemConfig = config.systemConfig
        self._cameraConfig = config.cameraConfig
        self._ioConfig = config.ioConfig
        self._clientConfig = config.clientConfig
        self._imageProcessorConfig = config.imageProcessorConfig
        self._stopStreamEvent = threading.Event()
        self._newDetectedImageAvailable = threading.Event() #set this event to notify webpage that a new detection has occured (so it can detect new detection image)
        self._define_routes()



    def _define_routes(self):
        """Define Flask routes using add_url_rule."""
        self.app.register_blueprint(create_motors_blueprint(self._motorControl, self._motorConfig))
        self.app.register_blueprint(create_imageProcessing_blueprint(self._detector, self._detector._imgProcessor))

        self.app.add_url_rule('/', 'serve_page', self.serve_page)
        #stream control
        self.app.add_url_rule('/stream', 'start_stream', self.startStream)
        self.app.add_url_rule('/base-img', 'base_img', self.returnBaseImg)
        self.app.add_url_rule('/detect-img', 'detect_img', self.returnDetectImg)
        self.app.add_url_rule('/stopStream', 'stopStream', self.stopStream)

        #sse endpoints
        self.app.add_url_rule("/dataEventSoruce", 'event1', self.sendDataSSE)
        self.app.add_url_rule("/detectNotifySource", 'event2', self.detectedImageSSE)        
        self.app.add_url_rule("/motorLocation", 'sendMotorLocation', self.sendMotorLocation)

        #system control endpoints
        self.app.add_url_rule("/forceDetection/<xRatio>/<yRatio>", 'forceDetect', self.forceDetection)
        self.app.add_url_rule("/actOnDetection/<onOff>", 'actOnDetection', self.actOnDetection)


    def serve_page(self):
        return flask.render_template("Picamera2Page.html")
    
    #Stream control
    def startStream(self):
        print("Starting stream")
        self._stopStreamEvent.clear()
        return flask.Response(self.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
    def stopStream(self):
        """Stop streaming frames"""
        print("setting stop event")
        self._stopStreamEvent.set()
        return "OkeY DoKEy", 200
    
    def returnBaseImg(self):
        pilImg = Image.fromarray(self._detector._imgProcessor._baseImg)
        ioImg = BytesIO()
        pilImg.save(ioImg, 'JPEG')
        ioImg.seek(0)
        return flask.send_file(ioImg, mimetype='image/jpeg')
    
    def returnDetectImg(self):
        print(self._detector._imgProcessor.detectImg.shape)
        pilImg = Image.fromarray(self._detector._imgProcessor.detectImg)
        ioImg = BytesIO()
        pilImg.save(ioImg, 'JPEG')
        ioImg.seek(0)
        return flask.send_file(ioImg, mimetype='image/jpeg')
    
    #system control
    def forceDetection(self, xRatio: str, yRatio: str):
        #clicked x ratio is backwards from camera detected x ratio, so reverse it before sending to detector
        xRatio = -1 * float(xRatio)
        yRatio = float(yRatio)
        self._detector.setDetectedRatio(float(xRatio), float(yRatio))
        return "okey DOKEY", 200

    def actOnDetection(self, onOff: str):
        if(onOff == "true"):
            self._systemConfig.actOnDetection = True
        else:
            self._systemConfig.actOnDetection = False
        return "okeY DoKEy", 200
    




    #server sent events
    def sendDataSSE(self): #Periodic data transfer
        return flask.Response(self.generate_data(), content_type='text/event-stream')

    def detectedImageSSE(self):
        return flask.Response(self.detectionNotificationStream(), content_type='text/event-stream')

    def sendMotorLocation(self):
        return flask.Response(self.getMotorPosition(), content_type='text/event-stream')

#Helper methods to endpoint methods
    def gen_frames(self):
        """Stream method that returns processed jpeg images in html response format"""
        while not self._stopStreamEvent.is_set():
            with self._imageSource.condition:
                self._imageSource.condition.wait() #Waits for the imageSource to be renewed
                yield (b'--frame\r\n' 
                b'Content-Type: image/jpeg\r\n\r\n' + self._imageSource.frame + b'\r\n') 

    def generate_data(self):
        while True:
            data = {
                'time': time.ctime(),
                'streaming': not self._stopStreamEvent.is_set(),
                'moddingImage': self._detector.processImage,
                'actOnDetection': self._systemConfig.actOnDetection,
                'xDegreesPerPercent': self._systemConfig.panDegreesPerCamPercentChange,
                'yDegreesPerPercent': self._systemConfig.tiltDegreesPerCamPercentChange
            }
            json_data = json.dumps(data)
            yield f"data: {json_data}\n\n"
            time.sleep(1)

    def detectionNotificationStream(self):
        while True:
            self._newDetectedImageAvailable.wait()
            self._newDetectedImageAvailable.clear()
            yield f"data: detected\n\n"

    def getMotorPosition(self):
        while True:
            #get all motor positions every # seconds
            #self.motionEnded.wait()
            #self.motionEnded.clear()
            data = {
                'xPosition': self._motorControl.GetMotorPos(MotorEnum.Pan),
                'yPosition': self._motorControl.GetMotorPos(MotorEnum.Tilt),
                'servoPosition': self._motorControl.GetMotorPos(MotorEnum.Chamber),
                'taughtOpen': self._motorConfig.chamberServo.openAngle,
                'taughtClosed': self._motorConfig.chamberServo.closedAngle
            }
            json_data = json.dumps(data)
            yield f"data: {json_data}\n\n"
            time.sleep(1)

    def OnMotionFound(self, location: tuple[int,int], callback: Callable[[bool], None]): 
        self._newDetectedImageAvailable.set()
        callback(True)


    #App control methods
    def startServer(self):
        """Run the Flask server."""
        #access page via 10.0.0.40:5000, localhost:5000, 127.0.0.1:5000
        self.app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)