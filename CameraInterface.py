from abc import ABC, abstractmethod

class CameraInterface(ABC):  
    def __init__(self):
        self.Picamera2 = CameraInterface.IPicamera2()

    class IPicamera2():
        def __init__(self):
            self.post_callback = None
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
            
    class encoders:
        class MJPEGEncoder():
            def __init__(self):
                pass

    class outputs:
        class FileOutput():
            def __init__(self):
                pass