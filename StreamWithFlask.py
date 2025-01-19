import io
import picamera2
import numpy
from PIL import Image
import flask


app = flask.Flask(__name__)


class DataStore():
    def __init__(self):
        self._runMode = True
        self.observers = []

    @property
    def runMode(self):
        return self._runMode
    
    @runMode.setter
    def data(self, value):
        self._runMode = value

dataStore = DataStore()


#image processing done here - get whatever data needed from image, modify it, and return the modified image
def process_frame(frame: numpy.array):
    image = Image.fromarray(frame)
    changed_image = Image.eval(image, lambda x: 255 - x)
    return numpy.array(changed_image)

#captures images and streams to web
'''def generate_frames():
    with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
        stream = io.BytesIO()
        for _ in camera.capture_continuous(stream, format="jpeg", use_video_port=True):
            stream.seek(0)
            image = Image.open(stream)
            
            frame = numpy.array(image)
            processed_frame = process_frame(frame)
            output_stream = io.BytesIO()
            Image.fromarray(processed_frame).save(output_stream, format="JPEG")
            frame = output_stream.getvalue()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            stream.truncate()  # Clear the stream for the next frame
            stream.seek(0)
            if(dataStore.runMode == False): 
                break'''

def Generate_Frames():
    with picamera2.Picamera2() as cam:
        stream = io.BytesIO()
        while True:
            frame = cam.capture_image() #capture_array()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            stream.truncate()  # Clear the stream for the next frame
            stream.seek(0)


@app.route('/')
def send_html():
    return flask.render_template("StreamOnlyPage.html")

@app.route('/stream.mjpg')
def video_feed():
    return flask.Response(Generate_Frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stopStream')
def stop_stream():
    print("Stopping Stream")
    dataStore.runMode = False

@app.route('/startStream')
def start_stream():
    print("Starting Stream")
    dataStore.runMode = True


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
