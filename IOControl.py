from IOInterface import IOInterface
class IOControl():
    def __init__(self, io : IOInterface):
        self.pi = io
        print("Pi detected = " + str(self.pi.connected))
    
    def SetPinMode(self, pin: int, mode: int):
        '''Set pin mode to input or output
            args:
                pin: (int) pin number to set
                mode: (int) 0=Input 1=Output
        '''
        self.pi.set_mode(pin, mode)

    def SetOutput(self, pin: int, value: bool):
        self.pi.write(pin, value)

    def SetPWMDutyCycle(self, pin: int, dutyCycle: int):
        '''Starts pwm on pin with specified duty cycle at 50Hz
            args:
                pin: (int) pin number to set
                dutyCycle: (int) 500-2500
        '''
        self.pi.set_servo_pulsewidth(pin, dutyCycle)
    
    def SetPWMFrequency(self, pin: int, frequency: int):
        self.pi.set_PWM_frequency(pin, frequency)
