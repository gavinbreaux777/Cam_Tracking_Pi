from fractions import Fraction
import concurrent.futures 
import threading

from typing import Tuple
from .StepperMotorControlInterface import StepperMotorControlInterface
from .RawStepperControl import RawStepperControl
from i_o.IOControl import IOControl
from config.ConfigClasses import SingleAimMotorConfig
from .Limits import Limits

class StepperMotorControl(StepperMotorControlInterface):
    '''
    Higher level stepper control class that deals in real-world units.
    Does not deal directly with io
    '''
    def __init__(self, ioControl: IOControl, config: SingleAimMotorConfig):
        self.motor = RawStepperControl(ioControl, config.stepPin, config.dirPin, config.enablePin, config.stepMode, config.stepsPerRev)
        self.speed = config.speed
        self._stepMode = float(Fraction(config.stepMode))
        self.motorResolution = config.stepsPerRev
        self.timeout = 10 #setting really high right now because we're not using rn. (client *should resend jog command before shorter timeout but currently only sending 1 start and 1 stop command from client)
        self._jogTimer = threading.Timer(self.timeout, self.StopMotors)
        self._hasBeenHomed = False
        self._limits = Limits()

    @property
    def hasBeenHomed(self) -> bool:
        '''True if home reference point has been set since startup'''
        return self._hasBeenHomed

    @property
    def limits(self) -> tuple[float, float]:
        '''Position limits in degrees (lower, upper)'''
        return (self._limits.lower, self._limits.upper)

    @property
    def enabled(self) -> bool:
        return self.motor.enabled
    @enabled.setter
    def enabled(self, value: bool):
        self.motor.enabled = value

    @property
    def position(self) -> float:
        '''In degrees'''
        return self.ConvertStepsToDegrees(self.motor.position)
    @position.setter
    def position(self, value: float):
        self.motor.position = value  
        
    @property
    def _stepsPerRevoluton(self):
        ''''''
        return self.motorResolution / self._stepMode

    @property
    def _stepsPerDegree(self):
        return self._stepsPerRevoluton / 360 
    
    @property
    def speed(self) -> float:
        '''speed of motor rotation in degrees/sec (actual speed ~15% slower than commanded per initial tests)'''
        return self._speed
    
    @speed.setter
    def speed(self, degPerSec):
        print("Setting speed in StepeprMotorControl")
        self._speed = degPerSec

    @property
    def _delayBetweenSteps(self):
        '''Time in seconds between consecutive step pulses'''
        return self.CalculateDelayBetweenSteps(self.speed)
    
    @property
    def accel(self, degreesPerSecondSquared: float):
        '''Currently not in use'''
        pass

    def CalculateDelayBetweenSteps(self, speedIn_ms):
        return 1 / speedIn_ms / (self._stepsPerDegree)

    def ConvertDegreesToSteps(self, degrees: float) -> int:
        return int(degrees * self._stepsPerDegree)
    
    def ConvertStepsToDegrees(self, steps: int) -> float:
        return float(steps / self._stepsPerDegree)

    def RotateRel(self, degrees: float) -> bool:
        """
        Rotate motor relative to current position
        Args:
            degrees: degrees to rotate (positive is clockwise)

        returns: true if made position, false if not
        """
        if(degrees < 0):
            cw = False
        else: 
            cw = True
        stepsToTake = abs(self.ConvertDegreesToSteps(degrees))

        madePosition = self.motor.MotorRotate(cw, stepsToTake, self._delayBetweenSteps)
        return madePosition

    def RotateAbs(self, targetDegrees: float):
        """
        Rotate motor to absolute position in degrees
        Args:
            degrees: degrees target

        returns: true if made position, false if not
        """
        degreeChange = targetDegrees - self.position
        if(degreeChange < 0):
            cw = False
        else:
            cw = True            
        stepsToTake = abs(self.ConvertDegreesToSteps(degreeChange))

        madePosition = self.motor.MotorRotate(cw, stepsToTake, self._delayBetweenSteps)
        return madePosition

    def Stop(self):
        self.motor.StopMotor()

    def Jog(self, speed: int, cw: bool):
        "Start motor moving clockwise at specified speed"
        stepsToTake = 10000
        delayBetweenSteps = self.CalculateDelayBetweenSteps(speed)
        #Start a thread so the function can return immediately, but start a timer to stop motors if timeout met
        threadPool = concurrent.futures.ThreadPoolExecutor()
        threadPool.submit(self.motor.MotorRotate(cw, stepsToTake, delayBetweenSteps))
        self.RestartJogTimer()

    def RestartJogTimer(self):
        '''Cancels current timeout timer if active and starts a new one for the timeout duration'''
        self._jogTimer.cancel()
        self._jogTimer = threading.Timer(self.timeout, self.StopMotors)
        self._jogTimer.start()

    def StopMotors(self):
        self.Stop()
        self._jogTimer.cancel()

    def SetLimit(self, limit: float, isUpper: bool):
        '''
        Set either upper or lower limit in degrees
        
        Args:
            limit: position limit in degrees
            isUpper: true if setting upper limit, false if setting lower limit
        '''        
        stepLimit = self.ConvertDegreesToSteps(limit)
        print("Converted stepLimit = " + str(stepLimit))
        self.motor.SetLimit(stepLimit, isUpper)
        if isUpper:
            self._limits.upper = limit
        else:
            self._limits.lower = limit

    def SetLimits(self, limits: Tuple[float, float]):
        '''
        Set lower and upper limits in degrees
        
        Args:
            limits: position limits in degrees (lower, upper)
        '''
        print("Shouldnt be here")
        cwStepLimit = self.ConvertDegreesToSteps(limits[0])
        ccwStepLimit = self.ConvertDegreesToSteps(limits[1])
        
        self.motor.SetLimits((cwStepLimit, ccwStepLimit))
        self._limits.lower = limits[0]
        self._limits.upper = limits[1]

    def SetHomeReference(self):
        '''Set current position of motor as home reference point (0 degrees)'''
        self.motor.SetHomeReference()
        self._hasBeenHomed = True