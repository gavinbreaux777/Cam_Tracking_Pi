import RPi.GPIO as gpio
import time
from RawServoControl import RawServoControl

class FiringControl():
    def __init__(self):
        self.relayOnPin = 21
        gpio.setmode(gpio.BCM)
        gpio.setup(self.relayOnPin, gpio.OUT)

        self.servo = RawServoControl(12, 50)
        self.closedAngle = 180
        self.openAngle = 90
        self.servo.SetAngle(self.closedAngle)

    def SpoolMotors(self):
        '''Spins up dc motors'''
        gpio.output(self.relayOnPin, gpio.HIGH)

    def StopMotors(self):
        '''Stop dc motors'''
        gpio.output(self.relayOnPin, gpio.LOW)

    def FireSingle(self):
        '''Release single ball. Motors should be spooled already'''
        self.servo.SetAngle(self.openAngle)
        time.sleep(.5) #Add sensor to allow only 1 ball?
        self.servo.SetAngle(self.closedAngle) 

    def FireContinuous(self):
        '''Open gate to release all balls'''
        self.servo.SetAngle(self.openAngle)

    def StopFiring(self):
        '''Close gat to stop releasing balls'''
        self.servo.SetAngle(self.closedAngle)




#pwmPin = 12
#gpio.setmode(gpio.BCM)
#gpio.setup(pwmPin, gpio.OUT)
#pwm = gpio.PWM(pwmPin, 50)
#pwm.start()
#time.sleep(3)
#pwm.stop()