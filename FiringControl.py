import RPi.GPIO as gpio
import time

#pwmPin = 12
#gpio.setmode(gpio.BCM)
#gpio.setup(pwmPin, gpio.OUT)
#pwm = gpio.PWM(pwmPin, 50)
#pwm.start()
#time.sleep(3)
#pwm.stop()

class FiringControl():
    def __init_(self):
        pwmPin = 12
        gpio.setmode(gpio.BCM)
        gpio.setup(pwmPin, gpio.OUT)
