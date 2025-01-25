import RPi.GPIO as gpio
import time
import RpiMotorLib
import RpiMotorLib.RpiMotorLib

gpio.setmode(gpio.BCM)
gpio.setup(18, gpio.OUT)
#gpio.output(18, gpio.HIGH)
#time.sleep(2)
#gpio.output(18, gpio.LOW)

#for i in range(200):
#    gpio.output(18, gpio.HIGH)
#    time.sleep(0.01)
#    gpio.output(18, gpio.LOW)

myMotor = RpiMotorLib.RpiMotorLib.A4988Nema(17, 18, (15,16,22), "A4988")

myMotor.motor_go()