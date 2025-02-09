import RPi.GPIO as gpio
import time
import RpiMotorLib.RpiMotorLib as RpiMotLib
import concurrent.futures 
from StepperMotorControlInterface import StepperMotorControlInterface
import threading

#gpio.setmode(gpio.BCM)
#gpio.setup(18, gpio.OUT)
#gpio.output(18, gpio.HIGH)
#time.sleep(2)
#gpio.output(18, gpio.LOW)

#for i in range(200):
#    gpio.output(18, gpio.HIGH)
#    time.sleep(0#.01)
#    gpio.output(18, gpio.LOW)

#myMotor = RpiMotLib.A4988Nema(1, 18, (-1,-1,-1), "A4988")

##myMotor.motor_go()

#threadPool = concurrent.futures.ThreadPoolExecutor()
#future1 = threadPool.submit(myMotor.motor_go, 0, "Full", 200, 0.005, False, .1)
#future2 = threadPool.submit(time.sleep, 1)
#done, not_done = concurrent.futures.wait([future1, future2], timeout=0.01)

class StepperMotorControl(StepperMotorControlInterface):
    def __init__(self, stepPin: int, dirPin: int = 1, stepResPins: tuple[int, int, int] = (-1,-1,-1), ):
        ''''''
        gpio.setmode(gpio.BCM)
        gpio.setup(stepPin, gpio.OUT)
        gpio.setup(dirPin, gpio.OUT)
        self.motor = RpiMotLib.A4988Nema(dirPin, stepPin, stepResPins, "A4988")
        self.stepFraction = 1
        self.motorResolution = 200
        self._position = 0
        self._speed = 120 
        self.timeout = 10 #setting really high right now because we're not using rn. (client *should resend jog command before shorter timeout but currently only sending 1 start and 1 stop command from client)
        self._jogTimer = threading.Timer(self.timeout, self.StopMotors)


    @property
    def position(self) -> int:
        '''In degrees'''
        return self._position
    @position.setter
    def position(self, value: int):
        self._position = value

    @property
    def _stepsPerRevoluton(self):
        ''''''
        return self.motorResolution * self.stepFraction
    
    @property
    def _stepsPerDegree(self):
        return self._stepsPerRevoluton / 360    
    
    @property
    def stepType(self):
        if(self.stepFraction == 1):
            return "Full"
        
    @property
    def speed(self) -> float:
        '''speed of motor rotation in degrees/sec (actual speed ~15% slower than commanded per initial tests)'''
        return self._speed
    
    @speed.setter
    def speed(self, degPerSec):
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
        return 1 / speedIn_ms * (self.motorResolution/360)

    def RotateRel(self, degrees: float) -> None:
        if(degrees < 0):
            cw = False
        else: 
            cw = True
        stepsToTake = (int)(degrees * self._stepsPerDegree)
        stepsToTake = abs(stepsToTake)
        self.motor.motor_go(clockwise=cw, steptype=self.stepType, steps=stepsToTake, stepdelay=self._delayBetweenSteps)

        self.position += degrees

    def RotateAbs(self, targetDegrees: float):
        stepsToTake = targetDegrees - self.position
        if(stepsToTake < 0):
            cw = False
        else:
            cw = True
        abs(stepsToTake)
        self.motor.motor_go(clockwise=cw, steptype=self.stepType, steps=stepsToTake, stepdelay=self._delayBetweenSteps )

        self.position = targetDegrees

    def Stop(self):
        self.motor.motor_stop()

    def Jog(self, speed: int, cw: bool):
        "Start motor moving clockwise at specified speed"
        stepsToTake = 10000
        delayBetweenSteps = self.CalculateDelayBetweenSteps(speed)
        #Start a thread so the function can return immediately, but start a timer to stop motors if timeout met
        threadPool = concurrent.futures.ThreadPoolExecutor()
        jogThread = threadPool.submit(self.motor.motor_go, clockwise=cw, steptype=self.stepType, steps=stepsToTake, stepdelay=delayBetweenSteps)
        self.RestartJogTimer()

    def RestartJogTimer(self):
        '''Cancels current timeout timer if active and starts a new one for the timeout duration'''
        self._jogTimer.cancel()
        self._jogTimer = threading.Timer(self.timeout, self.StopMotors)
        self._jogTimer.start()

    def StopMotors(self):
        self.Stop()
        self.Stop()