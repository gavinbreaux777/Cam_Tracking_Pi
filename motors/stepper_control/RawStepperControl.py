import time
from fractions import Fraction
from typing import Tuple
from .StepMode import StepMode
from i_o.IOControl import IOControl
from .Limits import Limits
class RawStepperControl():
    '''
    Low level stepper control class that deals in terms of steps and step timing. 
    Directly interfaces with IOControl
    '''
    def __init__(self, ioControl: IOControl, stepPin: int, directionPin: int = None, enablePin: int = None, stepMode: StepMode = StepMode.Full, stepsPerRev: int = 200):
        self._ioControl = ioControl
        self._ioControl.SetPinMode(stepPin, 1)
        self._ioControl.SetPinMode(directionPin, 1)
        self._directionPin = directionPin
        self._stepPin = stepPin
        self._stepMode = float(Fraction(stepMode))
        self._stopMotor = False
        self._stepsPerRev = stepsPerRev
        self._enabled = True
        self._enablePin = enablePin
        self.position = 0
        self._limits = Limits()

    @property
    def enabled(self) -> bool:
        return self._enabled
    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value
        if(self._enablePin == None):
            print("Enable pin not defined")
            return
        if(value == True):
            self._ioControl.SetOutput(self._enablePin, 0)
        else:
            self._ioControl.SetOutput(self._enablePin, 1)

    def MotorRotate(self, clockwise: bool, steps: int, stepDelay: float) -> bool:
        '''Rotate motor by specified number of steps
        Args: 
            clockwise: direction of rotation
            steps: number of steps to rotate
            stepDelay: delay between steps in milliseconds

            returns: true if made position, false if stopped early for limits
        '''
        self._stopMotor = False
        if(clockwise):
            self._ioControl.SetOutput(self._directionPin, 1)
        else:
            self._ioControl.SetOutput(self._directionPin, 0)
        try:
            for step in range(steps):
                if self._stopMotor == True or self.MoveNotAllowed(clockwise):
                    return False
                else:
                    self._ioControl.SetOutput(self._stepPin, 1)
                    time.sleep(stepDelay)
                    self._ioControl.SetOutput(self._stepPin, 0)
                    time.sleep(stepDelay)

                    if(clockwise == False):
                        self.position -= 1 #self._stepMode
                    else:
                        self.position += 1 #self._stepMode
            return True
                
        except Exception as ex:
            print("exception in RawStepperControl: " + str(ex))
            self.StopMotor()

    def StopMotor(self):
        #print("Stopping motor")
        self._stopMotor = True

    def SetLimits(self, limits: Tuple[float, float]):
        """
        Set CW and CCW limits in steps
        
        Args:
            limits: position limits in steps (CW limit, CCW limit)
        """
        self._limits.lower = limits[0]
        self._limits.upper = limits[1]

    def SetLimit(self, limit: float, isUpper: bool):
        '''
        Set either upper or lower limit in degrees
        
        Args:
            limit: position limit in degrees
            isUpper: true if setting upper limit, false if setting lower limit
        '''        
        if isUpper:
            self._limits.upper = limit
        else:
            self._limits.lower = limit

    def AtLimits(self) -> bool:
        '''Check if current position is at or beyond limits'''
        print("curPos = " + str(self.position) + " limits are: " + str(self._limits.lower) + " " + str(self._limits.upper))
        if(self._limits.lower is not None and self.position <= self._limits.lower):
            print("At limits: " + str(self.position) + " degrees. Limits are: " + str(self._limits))
            return True
        elif(self._limits.upper is not None and self.position >= self._limits.upper):
            print("At limits: " + str(self.position) + " degrees. Limits are: " + str(self._limits))
            return True
        else:
            return False
    
    def MoveNotAllowed(self, cwDirection: bool) -> bool:
        '''Check if motor allowed to move in direction per limits'''
        if(cwDirection and self.position >= self._limits.upper):
            return True
        elif(not cwDirection and self.position <= self._limits.lower):
            return True
        else:
            return False
    def SetHomeReference(self):
        "Set current position of motor as 0 steps"
        self.position = 0