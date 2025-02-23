from AimingControl import AimingControl
from FiringControl import FiringControl
from Observer import DetectionObserver
import time
import threading 
from typing import Tuple, Callable
class MotorControl(DetectionObserver):
    def __init__(self):
        #Create class to control aiming steppers
        self.aimingControl = AimingControl()
        self.firingControl = FiringControl()
        self.xCaliFactor = 1
        self.yCaliFactor = 1

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

    def OnMotionFound(self, location, acknowledgeCallback):
        '''Start thread to handle firing so image generation/processing can continue'''
        searchAndDestroyThread = threading.Thread(target=lambda: self.FindAndFire(location, acknowledgeCallback))
        searchAndDestroyThread.start()

    def FindAndFire(self, location: Tuple[int, int], callback: Callable[[bool], None]):
        '''Aim motors, fire projectile, and finally call callback to notify Detector that we've finished the sequence'''
        xAdjustment = location[0] * self.xCaliFactor
        yAdjustment = location[1] * self.yCaliFactor
        self.AimXYRel(xAdjustment, yAdjustment)
        #Spool motors and firing here
        #Notify detector that firing sequence finished
        callback(True)

        