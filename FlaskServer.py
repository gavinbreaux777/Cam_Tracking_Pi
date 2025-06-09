import flask
from flask import jsonify, make_response, json
import threading
from MotorControl import MotorControl
from Detector import Detector
from Observer import DetectionObserver
import time
from typing import Any, Callable, Tuple
from PIL import Image
from io import BytesIO

class FlaskServer(DetectionObserver):    
    '''Handles serving pages and image streams via Flask'''
    def __init__(self, detector: Detector, motorControl: MotorControl):
        '''
        Initialize FlaskServer
        
        Args:
            streamImageSource (StreamingOutput): The source of images to be streamed (this image will be streamed each time it is updated)
            stopProcessingImagesEvent (threading.Event): Event to raise when client requests stop of image processing
            motorControl (MotorControl): Class to pass client motor-control commands to
        '''
        self.app = flask.Flask(__name__)
        self.imageSource = detector.output
        self.baseImage = detector._imgProcessor._baseImg
        self.detector = detector
        self.motorControl = motorControl
        self.stopStreamEvent = threading.Event()
        self.newDetectedImageAvailable = threading.Event() #set this event to notify webpage that a new detection has occured (so it can detect new detection image)
        self.motionStarted = threading.Event()
        self.motionEnded = threading.Event()
        motorControl.motionStartedEvent.Subscribe(self.OnMotorStarted)
        motorControl.motionEndedEvent.Subscribe(self.OnMotorEnded)
        self._define_routes()



    def _define_routes(self):
        """Define Flask routes using add_url_rule."""
        self.app.add_url_rule('/', 'serve_page', self.serve_page)
        self.app.add_url_rule('/stream', 'start_stream', self.startStream)
        self.app.add_url_rule('/base-img', 'base_img', self.returnBaseImg)
        self.app.add_url_rule('/detect-img', 'detect_img', self.returnDetectImg)
        self.app.add_url_rule('/stopStream', 'stopStream', self.stopStream)
        self.app.add_url_rule("/stopImgMod", 'stopImgMod', self.stopImageModification)
        self.app.add_url_rule("/startImgMod", 'startImgMod', self.startImageModification)
        self.app.add_url_rule("/dataEventSoruce", 'event1', self.sendDataSSE)
        self.app.add_url_rule("/detectNotifySource", 'event2', self.detectedImageSSE)
        self.app.add_url_rule("/motorControl/<direction>/<speed>", 'motorControl', self.jogMotor)
        self.app.add_url_rule("/stopMotors", 'stopMotors', self.stopMotors)
        self.app.add_url_rule("/modImgProcSetting/<settingName>/<settingValue>", 'modImgProcSetting', self.setImageProcessSetting)
        self.app.add_url_rule("/modCamSetting/<settingName>/<settingValue>", 'modCamSetting', self.setCameraSetting)
        self.app.add_url_rule("/motorLocation", 'sendMotorLocation', self.sendMotorLocation)
        self.app.add_url_rule("/calibrateMotors/<xDegreesToPercentChange>/<yDegreesToPercentChange>", 'calibMotor', self.CalibrateMotors)
        self.app.add_url_rule("/moveChamberServo/<angle>", 'moveChamberServo', self.moveChamberServo)
        self.app.add_url_rule("/forceDetection/<xRatio>/<yRatio>", 'forceDetect', self.forceDetection)
        self.app.add_url_rule("/toggleDelta/<show>", 'toggleDelta', self.toggleDelta)
        self.app.add_url_rule("/toggleContours/<show>", 'toggleContours', self.toggleContours)
        self.app.add_url_rule("/enableDisableMotor/<motorStr>/<clicked>", 'enableDisableMotor', self.enableDisableMotor)
        self.app.add_url_rule("/enableDisableDCMotor/<clicked>", 'enableDisableDCMotor', self.enableDisableDCMotors)
        self.app.add_url_rule("/spoolDCMotors", 'spoolDCMotors', self.spoolDCMotors)
        self.app.add_url_rule("/stopDCMotors", 'stopDCMotors', self.stopDCMotors)
        self.app.add_url_rule("/actOnDetection/<onOff>", 'actOnDetection', self.actOnDetection)

#Endpoint methods for flask endpoints
    def serve_page(self):
        return flask.render_template("Picamera2Page.html")
    
    
    #Stream control
    def startStream(self):
        print("Starting stream")
        self.stopStreamEvent.clear()
        return flask.Response(self.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
    def stopStream(self):
        """Stop streaming frames"""
        print("setting stop event")
        self.stopStreamEvent.set()
        return "OkeY DoKEy", 200
    
    def returnBaseImg(self):
        pilImg = Image.fromarray(self.detector._imgProcessor._baseImg)
        ioImg = BytesIO()
        pilImg.save(ioImg, 'JPEG')
        ioImg.seek(0)
        return flask.send_file(ioImg, mimetype='image/jpeg')
    
    def returnDetectImg(self):
        pilImg = Image.fromarray(self.detector._imgProcessor.detectImg)
        ioImg = BytesIO()
        pilImg.save(ioImg, 'JPEG')
        ioImg.seek(0)
        return flask.send_file(ioImg, mimetype='image/jpeg')

    #Image processing control
    def stopImageModification(self):
        self.detector.processImage = False
        return "OkeY DoKEy", 200

    def startImageModification(self):
        self.detector.processImage = True
        return "OkeY DoKEy", 200
    
    def setImageProcessSetting(self, settingName: str, settingValue: Any):
        self.detector.ModifyImageProcessorSetting(settingName, settingValue)
        return "okey dokey then", 200

    def toggleDelta(self, show):
        if(show == "true"):
            self.detector.showDelta = True
        else:
            self.detector.showDelta = False
        return "OKeY DOkeY", 200

    def toggleContours(self, show):
        if(show == "true"):
            self.detector.showContours = True
        else:
            self.detector.showContours = False
        return "OKeY DOkeY", 200

    #Camera controls
    def setCameraSetting(self, settingName: str, settingValue: Any):
        self.detector.ModifyCameraSetting(settingName, settingValue)
        return "oKeY DoKEy thEN", 200
    
    def jogMotor(self, direction: str, speed: str):
        speedInt = int(speed)
        if(direction == "left"):
            self.motorControl.JogX(speedInt, True)
        elif(direction == "right"):
            self.motorControl.JogX(speedInt, False)
        elif(direction == "up"):
            self.motorControl.JogY(speedInt, True)
        elif(direction == "down"):
            self.motorControl.JogY(speedInt, False)
        else:
            print("Invalid direction parameter received: " + direction)
        return "Okey Dokey", 200
    
    def moveChamberServo(self, angle: str):
        angleInt = int(angle)
        print("moving servo")
        self.motorControl.SetChamberServoAngle(angleInt)
        return "okeY DOkey", 200

    def stopMotors(self):
        self.motorControl.StopMotors()
        return "okeY DokeY", 200

    def CalibrateMotors(self, xDegreesToPercentChange: float, yDegreesToPercentChange: float):
        self.motorControl.xDegreesPerPercentChange = float(xDegreesToPercentChange)
        self.motorControl.yDegreesPerPercentChange = float(yDegreesToPercentChange)
        print(str(xDegreesToPercentChange) + " , " + str(yDegreesToPercentChange))
        return "Okey Dokey", 200

    def forceDetection(self, xRatio: str, yRatio: str):
        self.detector.setDetectedRatio(float(xRatio), float(yRatio))
        return "okey DOKEY", 200

    def enableDisableMotor(self, motorStr: str, clicked: str):
        if(motorStr == "x"):
            if(clicked == "true"):
                self.motorControl.xMotorEnabled = True
            else:
                self.motorControl.xMotorEnabled = False
        elif(motorStr == "y"):
            if(clicked == "true"):
                self.motorControl.yMotorEnabled = True
            else:
                self.motorControl.yMotorEnabled = False
        return "Okey Dokey", 200

    def enableDisableDCMotors(self, clicked: str):
        if(clicked == "true"):
            self.motorControl.dcMotorControl.enabled = True
        else:
            self.motorControl.dcMotorControl.enabled = False
        return "OKEY dokeY", 200

    def spoolDCMotors(self):
        self.motorControl.dcMotorControl.SpoolMotorsWithTimeout()
        return "oKEY dokEY", 200

    def stopDCMotors(self):
        self.motorControl.dcMotorControl.StopMotors()
        return "OKeY DOKey", 200

    def actOnDetection(self, onOff: str):
        if(onOff == "true"):
            self.detector.actOnDetection = True
        else:
            self.detector.actOnDetection = False
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
        while not self.stopStreamEvent.is_set():
            with self.imageSource.condition:
                self.imageSource.condition.wait() #Waits for the imageSource to be renewed
                yield (b'--frame\r\n' 
                b'Content-Type: image/jpeg\r\n\r\n' + self.imageSource.frame + b'\r\n') 

    def generate_data(self):
        while True:
            data = {
                'time': time.ctime(),
                'streaming': not self.stopStreamEvent.is_set(),
                'moddingImage': self.detector.processImage,
                'actOnDetection': self.detector.actOnDetection,
                'xDegreesPerPercent': self.motorControl.xDegreesPerPercentChange,
                'yDegreesPerPercent': self.motorControl.yDegreesPerPercentChange,
            }
            json_data = json.dumps(data)
            yield f"data: {json_data}\n\n"
            time.sleep(1)

    def detectionNotificationStream(self):
        while True:
            self.newDetectedImageAvailable.wait()
            self.newDetectedImageAvailable.clear()
            yield f"data: detected\n\n"

    def getMotorPosition(self):
        while True:
            #self.motionEnded.wait()
            #self.motionEnded.clear()
            data = {
                'xPosition': self.motorControl.xPosition,
                'yPosition': self.motorControl.yPosition,
                'servoPosition': self.motorControl.chamberServoPosition
            }
            json_data = json.dumps(data)
            yield f"data: {json_data}\n\n"
            time.sleep(1)

    def OnMotionFound(self, location: tuple[int,int], callback: Callable[[bool], None], actOnDetection: bool): 
        self.newDetectedImageAvailable.set()
        callback(True)

    def OnMotorStarted(self):
        self.motionStarted.set()

    def OnMotorEnded(self):
        self.motionEnded.set()

    

    #App control methods
    def startServer(self):
        """Run the Flask server."""
        #access page via 10.0.0.40:5000, localhost:5000, 127.0.0.1:5000
        self.app.run(host='0.0.0.0', port=5000, debug=False)




