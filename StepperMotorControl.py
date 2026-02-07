from fractions import Fraction
import concurrent.futures 
from StepperMotorControlInterface import StepperMotorControlInterface
import threading
from RawStepperControl import RawStepperControl
from StepMode import StepMode
from IOControl import IOControl
from ConfigClasses import SingleAimMotorConfig

class StepperMotorControl(StepperMotorControlInterface):
    def __init__(self, ioControl: IOControl, config: SingleAimMotorConfig):
        ''''''
        self._ioControl = ioControl
        self._ioControl.SetPinMode(config.stepPin, 1)
        self._ioControl.SetPinMode(config.dirPin, 1)
        self.motor = RawStepperControl(ioControl, config.stepPin, config.dirPin, config.enablePin, config.stepMode, config.stepsPerRev)
        self.speed = config.speed
        self._stepMode = float(Fraction(config.stepMode))
        self.motorResolution = config.stepsPerRev
        self.timeout = 10 #setting really high right now because we're not using rn. (client *should resend jog command before shorter timeout but currently only sending 1 start and 1 stop command from client)
        self._jogTimer = threading.Timer(self.timeout, self.StopMotors)

    @property
    def enabled(self) -> bool:
        return self.motor.enabled
    @enabled.setter
    def enabled(self, value: bool):
        self.motor.enabled = value

    @property
    def position(self) -> float:
        '''In degrees'''
        return self.motor.position
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

    def RotateRel(self, degrees: float) -> None:
        if(degrees < 0):
            cw = False
        else: 
            cw = True
        stepsToTake = (int)(degrees * self._stepsPerDegree)
        stepsToTake = abs(stepsToTake)
        self.motor.MotorRotate(cw, stepsToTake, self._delayBetweenSteps)

    def RotateAbs(self, targetDegrees: float):
        stepsToTake = targetDegrees - self.position
        if(stepsToTake < 0):
            cw = False
        else:
            cw = True
        abs(stepsToTake)
        self.motor.MotorRotate(cw, stepsToTake, self._delayBetweenSteps)

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