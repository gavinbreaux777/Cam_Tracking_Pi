import RPi.GPIO as gpio
import time
import concurrent.futures 
from StepperMotorControlInterface import StepperMotorControlInterface
import threading
from RawStepperControl import RawStepperControl
from StepMode import StepMode
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


#from RawServoControl import RawServoControl
#servo = RawServoControl(12, 50)
#servo.SetAngle(180)
#time.sleep(2)

class StepperMotorControl(StepperMotorControlInterface):
    def __init__(self, stepPin: int, dirPin: int = 1, stepMode: StepMode = StepMode.Full):
        ''''''
        gpio.setmode(gpio.BCM)
        gpio.setup(stepPin, gpio.OUT)
        gpio.setup(dirPin, gpio.OUT)
        self.motor = RawStepperControl(stepPin, dirPin, stepMode, 200) 
        self._stepMode = stepMode
        self.motorResolution = 200
        self.speed = 120 
        self.timeout = 10 #setting really high right now because we're not using rn. (client *should resend jog command before shorter timeout but currently only sending 1 start and 1 stop command from client)
        self._jogTimer = threading.Timer(self.timeout, self.StopMotors)
        print("stepMode = " + str(self._stepMode))
        print("stepsPerRev = " + str(self._stepsPerRevoluton))
        print("stepsPerDegree = " + str(self._stepsPerDegree))
        print("delayBetweenSteps = " + str(self._delayBetweenSteps))


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