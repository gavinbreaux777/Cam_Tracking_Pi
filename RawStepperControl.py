import time
from StepMode import StepMode
from IOControl import IOControl
class RawStepperControl():

    def __init__(self, ioControl: IOControl, stepPin: int, directionPin: int = None, stepMode: StepMode = StepMode.Full, stepsPerRev: int = 200):
        self._ioControl = ioControl
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
            self._ioControl.SetOutput(self._directionPin, 1)
            #gpio.output(self._directionPin, gpio.HIGH)
        else:
            self._ioControl.SetOutput(self._directionPin, 0)
            #gpio.output(self._directionPin, gpio.LOW)
        try:
            for step in range(steps):
                if self._stopMotor == True:
                    break
                else:
                    self._ioControl.SetOutput(self._stepPin, 1)
                    time.sleep(stepDelay)
                    self._ioControl.SetOutput(self._stepPin, 0)
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