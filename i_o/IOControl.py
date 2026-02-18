from .IOInterface import IOInterface
from LoggerSetup import LoggerSetup

logger = LoggerSetup.get_logger("IOControl")

class IOControl():
    def __init__(self, io : IOInterface):
        self.pi = io
        logger.info(f"Pi detected = {self.pi.connected}")
        
    def SetPinMode(self, pin: int, mode: int):
        '''Set pin mode to input or output
            args:
                pin: (int) pin number to set
                mode: (int) 0=Input 1=Output
        '''
        mode_str = "Input" if mode == 0 else "Output"
        logger.debug(f"Setting pin {pin} mode to {mode_str}")
        self.pi.set_mode(pin, mode)

    def SetOutput(self, pin: int, value: bool):
        logger.debug(f"Setting pin {pin} output to {value}")
        self.pi.write(pin, value)

    def SetPWMDutyCycle(self, pin: int, dutyCycle: int):
        '''Starts pwm on pin with specified duty cycle at 50Hz
            args:
                pin: (int) pin number to set
                dutyCycle: (int) 500-2500
        '''
        logger.debug(f"Setting pin {pin} PWM duty cycle to {dutyCycle}")
        self.pi.set_servo_pulsewidth(pin, dutyCycle)
    
    def SetPWMFrequency(self, pin: int, frequency: int):
        logger.debug(f"Setting pin {pin} PWM frequency to {frequency} Hz")
        self.pi.set_PWM_frequency(pin, frequency)
