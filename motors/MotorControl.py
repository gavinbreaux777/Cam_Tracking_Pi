from .AimingControl import AimingControl
from helpers.Observer import DetectionObserver
from .MotorEnums import MotorEnum
from .FiringControl import FiringControl
from config.ConfigClasses import SystemConfig
import threading
from typing import Tuple, Callable
import time
class MotorControl(DetectionObserver):
    def __init__(self, aimingControl: AimingControl, firingControl: FiringControl, config: SystemConfig):
        self.aimingControl = aimingControl
        self.firingControl = firingControl
        self._config = config

#region universal commands
    def StopMotor(self, motorNum: MotorEnum):
        match motorNum:
            case MotorEnum.Pan | MotorEnum.Tilt:
                self.aimingControl.StopMotors()
            case MotorEnum.Spool:
                self.firingControl.StopMotors()
            case MotorEnum.Chamber:
                print("Stop not implemented for chamber servo")
            case _:
                print("Unknown motor")
        
    def MoveMotorRel(self, motorNum: MotorEnum, target: float):
        match motorNum:
            case MotorEnum.Pan:
                self.aimingControl.MoveXRel(target)
            case MotorEnum.Tilt:
                self.aimingControl.MoveYRel(target)
            case MotorEnum.Spool:
                print("Unable to move dc motor to target. Use Spool command instead")
            case MotorEnum.Chamber:
                print("Relative move not implemented for servos. Use absolute move")
            case _:
                print("Unknown motor")

    def MoveMotorAbs(self, motorNum: MotorEnum, target: float):
        match motorNum:
            case MotorEnum.Pan:
                self.aimingControl.MovePanAbs(target)
            case MotorEnum.Tilt:
                self.aimingControl.MoveTiltAbs(target)
            case MotorEnum.Spool:
                print("Unable to move dc motor to target. Use Spool command instead")
            case MotorEnum.Chamber:
                self.firingControl.SetChamberServoAngle(target)
            case _:
                print("Unknown motor")

    def JogMotor(self, motorNum: MotorEnum, speed: int, direction: bool):
        match motorNum:
            case MotorEnum.Pan:
                self.aimingControl.Jog(speed, direction, MotorEnum.Pan)
            case MotorEnum.Tilt:
                self.aimingControl.Jog(speed, direction, MotorEnum.Tilt)
            case MotorEnum.Spool:
                print("Unable to jog dc motor. Use Spool command instead")
            case MotorEnum.Chamber:
                print("Jog not implemented for chamber servo")
            case _:
                print("Unknown motor")
    
    def EnableMotor(self, motorNum: MotorEnum):
        match motorNum:
            case MotorEnum.Pan | MotorEnum.Tilt:
                self.aimingControl.EnableMotor(motorNum)
            case MotorEnum.Spool | MotorEnum.Chamber:
                self.firingControl.EnableMotor(MotorEnum.Spool)
            case _:
                print("Unknown motor")

    def DisableMotor(self, motorNum: MotorEnum):
        match motorNum:
            case MotorEnum.Pan | MotorEnum.Tilt:
                self.aimingControl.DisableMotor(motorNum)
            case MotorEnum.Spool | MotorEnum.Chamber:
                self.firingControl.DisableMotor(motorNum)
            case _:
                print("Unknown motor")

    def GetMotorPos(self, motorNum: MotorEnum) -> float:
        match motorNum:
            case MotorEnum.Pan | MotorEnum.Tilt:
                return self.aimingControl.motorPositions[motorNum]
            case MotorEnum.Spool:
                print("Invalid request: Unable to get position of dc motor")
            case MotorEnum.Chamber:
                return self.firingControl.motorPositions[motorNum]
            case _:
                print("Unknown motor")
#endregion


#region aimingControl commands
    def AimPanTiltRel(self, xDegrees: float, yDegrees: float):
        self.aimingControl.AimPanTiltRel(xDegrees, yDegrees)

    def OnMotionFound(self, location, acknowledgeCallback):
        '''Start thread to handle firing so image generation/processing can continue'''
        print("Motor control notified. Act on detection = " + str(self._config.actOnDetection))
        if(self._config.actOnDetection== True):
            print("starting motion thread")
            searchAndDestroyThread = threading.Thread(target=lambda: self.FindAndFire(location, acknowledgeCallback))
            searchAndDestroyThread.start()
            searchAndDestroyThread.join()

        #Notify detector that firing sequence is complete
        acknowledgeCallback(True)

    def FindAndFire(self, location: Tuple[int, int], callback: Callable[[bool], None]):
        '''Aim motors, fire projectile, and finally call callback to notify Detector that we've finished the sequence'''
        #detector give location in terms of offset from center of camera frame, based on camera resolution
        #convert from these pixel offsets to motor movements
        print("running find and fire")
        self.firingControl.SpoolMotors()

        xAdjustment, yAdjustment = self.CalculateMotorAdjustments(location)   
        print("aiming motors: " + str(xAdjustment) + " degrees x, " + str(yAdjustment) + " degrees y")
        self.AimPanTiltRel(xAdjustment, yAdjustment)
        print("Motors aimed, waiting for spool")
        while(not self.firingControl.motorsSpooled):
            pass
        print("Motors spooled, firing chamber servo")
        self.firingControl.ChamberSingle()
        time.sleep(0.2)
        self.firingControl.StopMotors()
    
    def CalculateMotorAdjustments(self, percentFromCenter: Tuple[int, int]) -> Tuple[float, float]:
        '''Convert from pixel offset-from-center of camera frame to motor degrees'''

        #Motor travel distance in degrees
        xAdjustment = percentFromCenter[0] * self._config.panDegreesPerCamPercentChange
        yAdjustment = percentFromCenter[1] * self._config.tiltDegreesPerCamPercentChange
        return xAdjustment, yAdjustment

    def SetTiltLimits(self, limits: Tuple[float, float]):
        """
        Set CW and CCW limits for tilt motor in degrees

        Args:
            limits: position limits in degrees (CW limit, CCW limit)
        """
        self.aimingControl.SetTiltMotorLimits(limits)

    def SetTiltLimit(self, limit: float, isUpper: bool):
        """
        Set either upper or lower limit for tilt motor in degrees

        Args:
            limit: position limit in degrees
            isUpper: true if setting upper limit, false if setting lower limit
        """
        self.aimingControl.SetTiltMotorLimit(limit, isUpper)

    def GetTiltLimits(self) -> Tuple[float, float]:
        '''Returns tilt motor limits in degrees (cw limit, ccw limit)'''
        return self.aimingControl.GetTiltLimits()

    def SetHomeReference(self):
        '''Set current position of motors as home reference point (0,0)'''
        self.aimingControl.SetHomeReference()

    def GetAimMotorsHomedStatus(self) -> bool:
        '''Return true if tilt motor has been homed since startup, false if not'''
        return self.aimingControl.hasBeenHomed
#endregion
    

#region firingControl commands
    def OpenChamberServo(self):
        self.firingControl.OpenChamberServo()

    def CloseChamberServo(self):
        self.firingControl.CloseChamberServo()

    def SpoolFiringMotors(self):
        self.firingControl.SpoolMotors()
#endregion