import time
import RPi.GPIO as gpio
from StepMode import StepMode
class RawStepperControl():

    def __init__(self, stepPin: int, directionPin: int = None, stepMode: StepMode = StepMode.Full, stepsPerRev: int = 200):
        self._directionPin = directionPin
        self._stepPin = stepPin
        self._stepMode = stepMode
        self._stopMotor = False
        self._stepsPerRev = stepsPerRev
        self.position = 0

    @property 
    def _degreesPerStep(self) -> float:
        return 360 / (self._stepsPerRev / self._stepMode)

    def MotorRotate(self, clockwise: bool, steps: int, stepDelay: float):
        '''Rotate motor by specified number of steps'''
        self._stopMotor = False
        if(clockwise):
            gpio.output(self._directionPin, gpio.HIGH)
        else:
            gpio.output(self._directionPin, gpio.LOW)
        try:
            for step in range(steps):
                if self._stopMotor == True:
                    break
                else:
                    gpio.output(self._stepPin, True)
                    time.sleep(stepDelay)
                    gpio.output(self._stepPin, False)
                    time.sleep(stepDelay)

                    if(clockwise == False):
                        self.position -= self._degreesPerStep
                    else:
                        self.position += self._degreesPerStep
                
        except Exception as ex:
            print("exception in RawStepperControl: " + str(ex))
            self.StopMotor()

    def StopMotor(self):
        print("Stopping motor")
        self._stopMotor = True