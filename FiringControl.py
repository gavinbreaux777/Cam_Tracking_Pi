import RPi.GPIO as gpio
import time
from RawServoControl import RawServoControl

#servo = RawServoControl(12, 50)
#servo.SetAngle(165)
#servo.SetAngle(160)
#time.sleep(0.1)
#servo.SetAngle(165)

class FiringControl():
    def __init__(self):
        self.relayOnPin = 21
        gpio.setmode(gpio.BCM)
        gpio.setup(self.relayOnPin, gpio.OUT)

        self.servo = RawServoControl(12, 50)
        self.closedAngle = 165
        self.openAngle = 160
        self.servo.SetAngle(self.closedAngle)

    @property
    def servoPosition(self) -> float:
        return self.servo.position

    def SpoolMotors(self):
        '''Spins up dc motors'''
        gpio.output(self.relayOnPin, gpio.HIGH)

    def StopMotors(self):
        '''Stop dc motors'''
        gpio.output(self.relayOnPin, gpio.LOW)

    def FireSingle(self):
        '''Release single ball. Motors should be spooled already'''
        self.servo.SetAngle(self.openAngle)
        time.sleep(0.1) #Add sensor to allow only 1 ball?
        self.servo.SetAngle(self.closedAngle) 

    def OpenGate(self):
        '''Open gate to release all balls'''
        self.servo.SetAngle(self.openAngle)

    def CloseGate(self):
        '''Close gate to stop releasing balls'''
        self.servo.SetAngle(self.closedAngle)

    def SetServoAngle(self, angle: float):
        self.servo.SetAngle(angle)



#pwmPin = 12
#gpio.setmode(gpio.BCM)
#gpio.setup(pwmPin, gpio.OUT)
#pwm = gpio.PWM(pwmPin, 50)
#pwm.start()
#time.sleep(3)
#pwm.stop()