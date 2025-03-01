import RPi.GPIO as gpio

class RawServoControl():
    def __init__(self, pwmPin, frequency: float):
        self._minAngle = 0
        self._maxAngle = 180
        self._minDutyCycle = 2
        self._maxDutyCycle = 12
        self._dutyCyclePerDegree = (self._maxDutyCycle - self._minDutyCycle) / (self._maxAngle - self._minAngle)

        gpio.setwarnings(False)
        gpio.setmode(gpio.BCM)
        gpio.setup(pwmPin, gpio.OUT)
        self._pwm = gpio.PWM(12, frequency)
        self._pwm.start(0)

    def SetAngle(self, angle: float):
        #Value range = 2 - 13 for angle = 0 - 180
        if(angle < self._minAngle or angle > self._maxAngle):
            print(f"Angle out of range. Range = {self._minAngle} - {self._maxAngle}")
            return
        dutyCycle = (angle * self._dutyCyclePerDegree) + 2
        self._pwm.ChangeDutyCycle(dutyCycle)