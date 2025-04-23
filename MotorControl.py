from IOControl import IOControl
from AimingControl import AimingControl
from FiringControl import FiringControl
from Observer import DetectionObserver
import time
import threading 
from typing import Tuple, Callable
from Event import Event
class MotorControl(DetectionObserver):
    def __init__(self, ioControl: IOControl):
        self.ioControl = ioControl
        #Create class to control aiming steppers
        self.aimingControl = AimingControl(self.ioControl)
        self.firingControl = FiringControl(self.ioControl)
        self.xDegreesPerPercentChange = 50 #CalifFactor - degrees motor move per % pixel change (% pixel change = (detect location - center location) / center location
        self.yDegreesPerPercentChange = 20
        self.motionStartedEvent = Event()
        self.motionEndedEvent = Event()

        self.aimingControl.motorSpeed = (100, 100)
        self.firingControl.CloseGate()

    @property
    def xMotorEnabled(self) -> bool:
        '''Enable or disable motor if enable pin defined. 0 = disable, 1 = enable'''
        return self.aimingControl.xMotor.enabled
    @xMotorEnabled.setter
    def xMotorEnabled(self, value: bool):
        self.aimingControl.xMotor.enabled = value

    @property
    def yMotorEnabled(self) -> bool:
        '''Enable or disable motor if enable pin defined. 0 = disable, 1 = enable'''
        return self.aimingControl.yMotor.enabled
    @yMotorEnabled.setter
    def yMotorEnabled(self, value: bool):
        self.aimingControl.yMotor.enabled = value

    @property
    def xPosition(self) -> float:
        return self.aimingControl.xPosition
    
    @property
    def yPosition(self) -> float:
        return self.aimingControl.yPosition
    
    @property
    def servoPosition(self) -> float:
        return self.firingControl.servoPosition

    def AimXYRel(self, xDegrees: float, yDegrees: float):
        self.aimingControl.AimXYRel(xDegrees, yDegrees)

    def MoveXRel(self, degrees: float):
        self.aimingControl.MoveXRel(degrees)

    def MoveYRel(self, degrees: float):
        self.aimingControl.MoveYRel(degrees)

    def JogX(self, speed: int, clockwise: bool):
        '''Command motor to move at constant speed until timeout reached, unless another command is received. Speed in mm/s'''
        self.aimingControl.Jog(speed, clockwise, 1)

    def JogY(self, speed: int, clockwise: bool):
        self.aimingControl.Jog(speed, clockwise, 2)

    def StopMotors(self):
        self.aimingControl.StopMotors()

    def OnMotionFound(self, location, acknowledgeCallback, actOnMotion: bool):
        '''Start thread to handle firing so image generation/processing can continue'''
        if(actOnMotion == True):
            searchAndDestroyThread = threading.Thread(target=lambda: self.FindAndFire(location, acknowledgeCallback))
            searchAndDestroyThread.start()
            searchAndDestroyThread.join()

        #Notify detector that firing sequence is complete
        acknowledgeCallback(True)

    def FindAndFire(self, location: Tuple[int, int], callback: Callable[[bool], None]):
        '''Aim motors, fire projectile, and finally call callback to notify Detector that we've finished the sequence'''
        self.firingControl.SpoolMotors()
        spoolStartTime = time.time()

        #pixel distance from center
        pixelXDistanceFromCenter = location[0] - (640/2)
        pixelYDistanceFromCenter = (480/2) - location[1]

        #Percent distance from center (far right, top = 1,1 ; far left and bottom = -1,-1)
        percentXDistanceFromCenter = pixelXDistanceFromCenter / (640/2)
        percentYDistanceFromCenter = pixelYDistanceFromCenter / (480/2)

        #Motor travel distance in degrees
        xAdjustment = percentXDistanceFromCenter * self.xDegreesPerPercentChange
        yAdjustment = percentYDistanceFromCenter * self.yDegreesPerPercentChange
        self.AimXYRel(xAdjustment, yAdjustment)
        while(time.time() - spoolStartTime < 2):
            pass
        
        self.firingControl.FireSingle()
        self.firingControl.StopMotors()


    def SetServoAngle(self, angle: float):
        self.firingControl.SetServoAngle(angle)


        