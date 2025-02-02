import flask
from flask import jsonify, make_response, json
import threading
from StreamingOutput import StreamingOutput
from MotorControl import MotorControl
import time

class FlaskServer:    
    '''Handles serving pages and image streams via Flask'''
    def __init__(self, streamImageSource: StreamingOutput, stopProcessingImagesEvent: threading.Event, motorControl: MotorControl):
        '''
        Initialize FlaskServer
        
        Args:
            streamImageSource (StreamingOutput): The source of images to be streamed (this image will be streamed each time it is updated)
            imageGenerator (ImageGenerator): Class controlling camera and creating images
            aimingControl (AimingControl): Class controlling aiming motors
        '''
        self.app = flask.Flask(__name__)
        self.imageSource = streamImageSource
        self.stopProcessingEvent = stopProcessingImagesEvent
        self.motorControl = motorControl
        self.stopStreamEvent = threading.Event()
        self._define_routes()


    def _define_routes(self):
        """Define Flask routes using add_url_rule."""
        self.app.add_url_rule('/', 'serve_page', self.serve_page)
        self.app.add_url_rule('/stream', 'start_stream', self.startStream)
        self.app.add_url_rule('/stopStream', 'stopStream', self.stopStream)
        self.app.add_url_rule("/stopImgMod", 'stopImgMod', self.stopImageModification)
        self.app.add_url_rule("/startImgMod", 'startImgMod', self.startImageModification)
        self.app.add_url_rule("/dataEventSoruce", 'events', self.sendData)
        self.app.add_url_rule("/motorControl/<direction>/<speed>", 'motorControl', self.jogMotor)
        self.app.add_url_rule("/stopMotors", 'stopMotors', self.stopMotors)


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
    

    #Image processing control
    def stopImageModification(self):
        self.stopProcessingEvent.set()
        return "OkeY DoKEy", 200

    def startImageModification(self):
        self.stopProcessingEvent.clear()
        return "OkeY DoKEy", 200
    
    #Data transfer
    def sendData(self):
        return flask.Response(self.generate_data(), content_type='text/event-stream')


    #Motor control
    def moveMotorRel(self, direction: str, distance: str):
        distanceInt = int(distance)
        if(direction == "left"):
            distanceInt *= -1
            self.motorControl.MoveXRel(distanceInt)
        elif(direction == "right"):
            self.motorControl.MoveXRel(distanceInt)
        else:
            print("Invalid direction parameter received: " + direction)
        return "Okey Dokey", 200
    
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
    
    def stopMotors(self):
        self.motorControl.StopMotors()
        return "okeY DokeY", 200

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
                'time': time.ctime()
            }
            json_data = json.dumps(data)
            yield f"data: {json_data}\n\n"
            time.sleep(5)



    #App control methods
    def startServer(self):
        """Run the Flask server."""
        #access page via 10.0.0.40:5000, localhost:5000, 127.0.0.1:5000
        self.app.run(host='0.0.0.0', port=5000, debug=False)




