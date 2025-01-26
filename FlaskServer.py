import flask
from flask import jsonify, make_response
import threading
from StreamingOutput import StreamingOutput

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
        self.app.add_url_rule('/stream', 'start_stream', self.startStream)
        self.app.add_url_rule('/stopStream', 'stopStream', self.stopStream)

    def stopStream(self):
        """Stop streaming frames"""
        print("setting stop event")
        return "Stream stopped"

    #Endpoint methods for flask endpoints
    def serve_page(self):
        return flask.render_template("Picamera2Page.html")
    
    def startStream(self):
        print("Starting stream")
        self.stopStreamEvent.clear()
        return flask.Response(self.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
    def stopStream(self):
        """Stop streaming frames"""
        print("setting stop event")
        self.stopStreamEvent.set()
        return "OkeY DoKEy", 200

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




