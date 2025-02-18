import RPi.GPIO as gpio
import time

class FiringControl():
    def __init__(self):
        self.relayOnPin = 21
        gpio.setmode(gpio.BCM)
        gpio.setup(self.relayOnPin, gpio.OUT)

    def SpoolMotors(self):
        '''Spins up dc motors'''
        gpio.output(self.relayOnPin, gpio.HIGH)

    def StopMotors(self):
        '''Stop dc motors'''
        gpio.output(self.relayOnPin, gpio.LOW)


#pwmPin = 12
#gpio.setmode(gpio.BCM)
#gpio.setup(pwmPin, gpio.OUT)
#pwm = gpio.PWM(pwmPin, 50)
#pwm.start()
#time.sleep(3)
#pwm.stop()