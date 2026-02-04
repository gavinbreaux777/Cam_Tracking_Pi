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
from MotorEnums import MotorEnum
from AppConfig import AppConfig

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
        self.app.add_url_rule("/stopAimMotors", 'stopAimMotors', self.stopAimMotors)
        self.app.add_url_rule("/modImgProcSetting/<settingName>/<settingValue>", 'modImgProcSetting', self.setImageProcessSetting)
        self.app.add_url_rule("/modCamSetting/<settingName>/<settingValue>", 'modCamSetting', self.setCameraSetting)
        self.app.add_url_rule("/motorLocation", 'sendMotorLocation', self.sendMotorLocation)
        self.app.add_url_rule("/calibrateMotors/<xDegreesToPercentChange>/<yDegreesToPercentChange>", 'calibMotor', self.CalibrateMotors)
        self.app.add_url_rule("/moveChamberServo/<angle>", 'moveChamberServo', self.moveChamberServo)
        self.app.add_url_rule("/openChamberServo", 'openChamberServo', self.openChamberServo)
        self.app.add_url_rule("/closeChamberServo", 'closeChamberServo', self.closeChamberServo)        
        self.app.add_url_rule("/teachServo/<state>", 'teachServo', self.teachServo)
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
        pilImg = Image.fromarray(self._detector._imgProcessor.detectImg)
        ioImg = BytesIO()
        pilImg.save(ioImg, 'JPEG')
        ioImg.seek(0)
        return flask.send_file(ioImg, mimetype='image/jpeg')

    #Image processing control
    def stopImageModification(self):
        self._detector.processImage = False
        return "OkeY DoKEy", 200

    def startImageModification(self):
        self._detector.processImage = True
        return "OkeY DoKEy", 200
    
    def setImageProcessSetting(self, settingName: str, settingValue: Any):
        setattr(self._imageProcessorConfig, settingName, settingValue)
        #self._detector.ModifyImageProcessorSetting(settingName, settingValue)
        return "okey dokey then", 200

    def toggleDelta(self, show):
        if(show == "true"):
            self._detector.showDelta = True
        else:
            self._detector.showDelta = False
        return "OKeY DOkeY", 200

    def toggleContours(self, show):
        if(show == "true"):
            self._detector.showContours = True
        else:
            self._detector.showContours = False
        return "OKeY DOkeY", 200

    #Camera controls
    def setCameraSetting(self, settingName: str, settingValue: Any):
        self._detector.ModifyCameraSetting(settingName, settingValue)
        return "oKeY DoKEy thEN", 200
    
    def jogMotor(self, direction: str, speed: str):
        speedInt = int(speed)
        match direction:
            case "left":
                self._motorControl.JogMotor(MotorEnum.Pan, speedInt, True)
            case "right":
                self._motorControl.JogMotor(MotorEnum.Pan, speedInt, False)
            case "up":
                self._motorControl.JogMotor(MotorEnum.Tilt, speedInt, True)
            case "down":
                self._motorControl.JogMotor(MotorEnum.Tilt, speedInt, False)
            case _:
                print("Invalid direction parameter received: " + direction)
                return "Invalid direction parameter", 400
        return "Okey Dokey", 200
    
    def moveChamberServo(self, angle: str):
        angleInt = float(angle)
        print("moving servo")
        self._motorControl.MoveMotor(MotorEnum.Chamber, angleInt)
        return "okeY DOkey", 200

    def openChamberServo(self):
        print("opening servo")
        self._motorControl.OpenChamberServo()
        return "okeY DOkey", 200
    
    def closeChamberServo(self):
        print("closing servo")
        self._motorControl.CloseChamberServo()
        return "okeY DOkey", 200

    def stopAimMotors(self):
        self._motorControl.StopMotor(MotorEnum.Pan)
        self._motorControl.StopMotor(MotorEnum.Tilt)
        return "okeY DokeY", 200

    def CalibrateMotors(self, xDegreesToPercentChange: float, yDegreesToPercentChange: float):
        self._motorConfig.aimMotors.panMotor = float(xDegreesToPercentChange)
        self._motorConfig.aimMotors.tiltMotor = float(yDegreesToPercentChange)
        print(str(xDegreesToPercentChange) + " , " + str(yDegreesToPercentChange))
        return "Okey Dokey", 200

    def forceDetection(self, xRatio: str, yRatio: str):
        self._detector.setDetectedRatio(float(xRatio), float(yRatio))
        return "okey DOKEY", 200

    def enableDisableMotor(self, motorStr: str, clicked: str):
        match motorStr:
            case "Pan":
                if(clicked == "true"):
                    self._motorControl.EnableMotor(MotorEnum.Pan)
                else:
                    self._motorControl.DisableMotor(MotorEnum.Pan)
            case "Tilt":
                if(clicked == "true"):
                    self._motorControl.EnableMotor(MotorEnum.Tilt)
                else:
                    self._motorControl.EnableMotor(MotorEnum.Tilt)
            case _:
                print("Unknown motor: " + motorStr)
                return "Unknown motor: " + motorStr, 400
        return "Okey Dokey", 200

    def enableDisableDCMotors(self, clicked: str):
        if(clicked == "true"):
            self._motorControl.EnableMotor(MotorEnum.Spool)         
        else:
            self._motorControl.DisableMotor(MotorEnum.Spool)
        return "OKEY dokeY", 200

    def spoolDCMotors(self):
        self._motorControl.SpoolFiringMotors()
        return "oKEY dokEY", 200

    def stopDCMotors(self):
        self._motorControl.StopMotor(MotorEnum.Spool)
        return "OKeY DOKey", 200

    def actOnDetection(self, onOff: str):
        if(onOff == "true"):
            self._systemConfig.actOnDetection = True
        else:
            self._systemConfig.actOnDetection = False
        return "okeY DoKEy", 200
    
    def teachServo(self, state: str):
        """Record the current chamber servo position as taught open/closed."""
        try:
            current_pos = self._motorControl.GetMotorPos(MotorEnum.Chamber)
            if state == 'open':
                self._motorConfig.chamberServo.openAngle = current_pos
            elif state == 'closed':
                self._motorConfig.chamberServo.closedAngle = current_pos
            else:
                return f"Unknown state: {state}", 400
            return "OK", 200
        except Exception as e:
            print(f"Error in teachServo: {e}")
            return "Error", 500



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

    def OnMotorStarted(self):
        #self.motionStarted.set()
        pass

    def OnMotorEnded(self):
        #self.motionEnded.set()
        pass

    

    #App control methods
    def startServer(self):
        """Run the Flask server."""
        #access page via 10.0.0.40:5000, localhost:5000, 127.0.0.1:5000
        self.app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)