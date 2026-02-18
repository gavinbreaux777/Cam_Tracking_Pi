from .AimingControl import AimingControl
from helpers.Observer import DetectionObserver
from .MotorEnums import MotorEnum
from .FiringControl import FiringControl
from config.ConfigClasses import SystemConfig
import threading
from typing import Tuple, Callable
import time
from LoggerSetup import LoggerSetup, log_function_call

logger = LoggerSetup.get_logger("MotorControl")
class MotorControl(DetectionObserver):
    def __init__(self, aimingControl: AimingControl, firingControl: FiringControl, config: SystemConfig):
        self.aimingControl = aimingControl
        self.firingControl = firingControl
        self._config = config

#region universal commands
    def StopMotor(self, motorNum: MotorEnum):
        match motorNum:
            case MotorEnum.Pan | MotorEnum.Tilt:
                logger.info(f"Stopping aiming motors")
                self.aimingControl.StopMotors()
                time.sleep(0.1)  # Brief delay for motors to settle
                logger.info(f"Pan position: {self.aimingControl.motorPositions[MotorEnum.Pan]:.2f}deg, Tilt position: {self.aimingControl.motorPositions[MotorEnum.Tilt]:.2f}deg")
            case MotorEnum.Spool:
                logger.info("Stopping firing motor (spool)")
                self.firingControl.StopMotors()
            case MotorEnum.Chamber:
                logger.debug("Stop not implemented for chamber servo")
            case _:
                logger.error("Unknown motor")
        
    def MoveMotorRel(self, motorNum: MotorEnum, target: float):
        match motorNum:
            case MotorEnum.Pan:
                old_pos = self.aimingControl.motorPositions[MotorEnum.Pan]
                logger.info(f"Moving Pan motor relatively by {target}deg (from {old_pos:.2f}deg)")
                self.aimingControl.MoveXRel(target)
                new_pos = self.aimingControl.motorPositions[MotorEnum.Pan]
                logger.info(f"Pan motor moved to {new_pos:.2f}deg")
            case MotorEnum.Tilt:
                old_pos = self.aimingControl.motorPositions[MotorEnum.Tilt]
                logger.info(f"Moving Tilt motor relatively by {target}deg (from {old_pos:.2f}deg)")
                self.aimingControl.MoveYRel(target)
                new_pos = self.aimingControl.motorPositions[MotorEnum.Tilt]
                logger.info(f"Tilt motor moved to {new_pos:.2f}deg")
            case MotorEnum.Spool:
                logger.error("Unable to move dc motor to target. Use Spool command instead")
            case MotorEnum.Chamber:
                logger.error("Relative move not implemented for servos. Use absolute move")
            case _:
                logger.error("Unknown motor")

    def MoveMotorAbs(self, motorNum: MotorEnum, target: float):
        match motorNum:
            case MotorEnum.Pan:
                logger.info(f"Moving Pan motor to {target:.2f}deg")
                self.aimingControl.MovePanAbs(target)
                final_pos = self.aimingControl.motorPositions[MotorEnum.Pan]
                logger.info(f"Pan motor is now at {final_pos:.2f}deg")
            case MotorEnum.Tilt:
                logger.info(f"Moving Tilt motor to {target:.2f}deg")
                self.aimingControl.MoveTiltAbs(target)
                final_pos = self.aimingControl.motorPositions[MotorEnum.Tilt]
                logger.info(f"Tilt motor is now at {final_pos:.2f}deg")
            case MotorEnum.Spool:
                logger.error("Unable to move dc motor to target. Use Spool command instead")
            case MotorEnum.Chamber:
                logger.info(f"Moving Chamber servo to {target:.2f}deg")
                self.firingControl.SetChamberServoAngle(target)
                final_pos = self.firingControl.motorPositions[MotorEnum.Chamber]
                logger.info(f"Chamber servo is now at {final_pos:.2f}deg")
            case _:
                logger.error("Unknown motor")

    def JogMotor(self, motorNum: MotorEnum, speed: int, direction: bool):
        direction_str = "forward" if direction else "reverse"
        match motorNum:
            case MotorEnum.Pan:
                logger.info(f"Jogging Pan motor {direction_str} at speed {speed}")
                self.aimingControl.Jog(speed, direction, MotorEnum.Pan)
            case MotorEnum.Tilt:
                logger.info(f"Jogging Tilt motor {direction_str} at speed {speed}")
                self.aimingControl.Jog(speed, direction, MotorEnum.Tilt)
            case MotorEnum.Spool:
                logger.error("Unable to jog dc motor. Use Spool command instead")
            case MotorEnum.Chamber:
                logger.error("Jog not implemented for chamber servo")
            case _:
                logger.error("Unknown motor")
    
    def EnableMotor(self, motorNum: MotorEnum):
        match motorNum:
            case MotorEnum.Pan | MotorEnum.Tilt:
                logger.info(f"Enabling aiming motor: {motorNum}")
                self.aimingControl.EnableMotor(motorNum)
            case MotorEnum.Spool | MotorEnum.Chamber:
                logger.info(f"Enabling firing motor: {motorNum}")
                self.firingControl.EnableMotor(MotorEnum.Spool)
            case _:
                logger.error("Unknown motor")

    def DisableMotor(self, motorNum: MotorEnum):
        match motorNum:
            case MotorEnum.Pan | MotorEnum.Tilt:
                logger.info(f"Disabling aiming motor: {motorNum}")
                self.aimingControl.DisableMotor(motorNum)
            case MotorEnum.Spool | MotorEnum.Chamber:
                logger.info(f"Disabling firing motor: {motorNum}")
                self.firingControl.DisableMotor(motorNum)
            case _:
                logger.error("Unknown motor")

    def GetMotorPos(self, motorNum: MotorEnum) -> float:
        match motorNum:
            case MotorEnum.Pan | MotorEnum.Tilt:
                pos = self.aimingControl.motorPositions[motorNum]
                return pos
            case MotorEnum.Spool:
                logger.error("Invalid request: Unable to get position of dc motor")
            case MotorEnum.Chamber:
                pos = self.firingControl.motorPositions[motorNum]
                return pos
            case _:
                logger.error("Unknown motor")
#endregion


#region aimingControl commands
    def AimPanTiltRel(self, xDegrees: float, yDegrees: float):
        self.aimingControl.AimPanTiltRel(xDegrees, yDegrees)

    def OnMotionFound(self, location, acknowledgeCallback):
        '''Start thread to handle firing so image generation/processing can continue'''
        logger.info(f"Motion detected at location {location}. Act on detection = {self._config.actOnDetection}")
        if(self._config.actOnDetection == True):
            logger.info("Starting firing sequence thread")
            searchAndDestroyThread = threading.Thread(target=lambda: self.FindAndFire(location, acknowledgeCallback))
            searchAndDestroyThread.start()
            searchAndDestroyThread.join()

        #Notify detector that firing sequence is complete
        acknowledgeCallback(True)

    def FindAndFire(self, location: Tuple[int, int], callback: Callable[[bool], None]):
        '''Aim motors, fire projectile, and finally call callback to notify Detector that we've finished the sequence'''
        #detector give location in terms of offset from center of camera frame, based on camera resolution
        #convert from these pixel offsets to motor movements
        logger.info("Starting Find and Fire sequence")
        self.firingControl.SpoolMotors()

        xAdjustment, yAdjustment = self.CalculateMotorAdjustments(location)   
        logger.info(f"Calculated motor adjustments - Pan: {xAdjustment} degrees, Tilt: {yAdjustment} degrees")
        self.AimPanTiltRel(xAdjustment, yAdjustment)
        logger.debug("Motors aimed, waiting for spool")
        while(not self.firingControl.motorsSpooled):
            pass
        logger.info("Motors spooled, firing chamber servo")
        self.firingControl.ChamberSingle()
        time.sleep(0.2)
        self.firingControl.StopMotors()
        logger.info("Find and Fire sequence complete")
    
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