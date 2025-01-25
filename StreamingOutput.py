import threading
import io

class StreamingOutput(io.BufferedIOBase):
    '''io class representing stream coming directly from camera'''
    def __init__(self):
        self.frame = None
        self.condition = threading.Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()