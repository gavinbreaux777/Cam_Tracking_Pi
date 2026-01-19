from abc import ABC, abstractmethod
class IOInterface():    
    def __init__(self):
        self.connected = True
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

    @abstractmethod
    def set_PWM_frequency(*args):
        pass
