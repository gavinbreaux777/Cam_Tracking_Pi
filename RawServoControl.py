from IOControl import IOControl

class RawServoControl():
    def __init__(self, ioControl: IOControl, pwmPin, frequency: float):
        self.ioControl = ioControl
        self._pwmPin = pwmPin
        self._minAngle = 0
        self._maxAngle = 180
        self._minDutyCycle = 500
        self._maxDutyCycle = 2500
        self._dutyCyclePerDegree = (self._maxDutyCycle - self._minDutyCycle) / (self._maxAngle - self._minAngle)
        self.position = 0

        self.ioControl.SetPinMode(pwmPin, 1)
        self.ioControl.SetPWMFrequency(self._pwmPin, frequency)
        self.SetAngle(self._minAngle)

    def SetAngle(self, angle: float):
        if(angle < self._minAngle or angle > self._maxAngle):
            print(f"Angle out of range. Range = {self._minAngle} - {self._maxAngle}")
            return
        dutyCycle = int(500 + (angle * self._dutyCyclePerDegree))
        self.ioControl.SetPWMDutyCycle(self._pwmPin, dutyCycle)
        self.position = angle