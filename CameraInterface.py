from abc import ABC, abstractmethod

class CameraInterface(ABC):  
    def __init__(self):
        self.camera = CameraInterface.picamera2()
        self.post_callback = None

    class picamera2():
        @abstractmethod
        def configure(*args):
            pass

        @abstractmethod
        def set_controls(*args):
            pass

        @abstractmethod
        def start_recording(*args):
            pass

        @abstractmethod
        def stop_recording():
            pass

        @abstractmethod
        def capture_array():
            pass

        @abstractmethod
        def create_video_configuration(*args):
            pass
        
    class MappedArray():
        def __init__(self):
            self.array = []
            
        