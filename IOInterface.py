from abc import ABC, abstractmethod
class IOInterface():    
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def set_mode(*args):
        pass
    
    @abstractmethod
    def write(*args):
        pass

    @abstractmethod
    def set_servo_pulsewidth(*args):
        pass
