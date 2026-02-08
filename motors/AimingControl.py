from concurrent import futures
from typing import Tuple
from .stepper_control.StepperMotorControl import StepperMotorControl
from .MotorEnums import MotorEnum

class AimingControl():
    def __init__(self, panMotor: StepperMotorControl, tiltMotor: StepperMotorControl):
        self.panMotor = panMotor
        self.tiltMotor = tiltMotor
        self.threadPool = futures.ThreadPoolExecutor()

    @property
    def motorPositions(self) -> dict[MotorEnum, float]:
        pos = {}
        pos[MotorEnum.Pan] = self.panMotor.position
        pos[MotorEnum.Tilt] = self.tiltMotor.position
        return pos

    @property
    def motorSpeeds(self) -> dict[MotorEnum, float]: 
        '''Speed for both motors in degPerSec'''
        speeds = {}
        speeds[MotorEnum.Pan] = self.panMotor.speed
        speeds[MotorEnum.Tilt] = self.tiltMotor.speed
        return speeds
    
    @motorSpeeds.setter
    def motorSpeeds(self, panTiltSpeeds: Tuple[float, float]):
        self.panMotor.speed = panTiltSpeeds[0]
        self.tiltMotor.speed = panTiltSpeeds[1]

    @property
    def hasBeenHomed(self) -> bool:
        '''true if both motors (pan and tilt) report they have been homed'''
        return self.panMotor.hasBeenHomed and self.tiltMotor.hasBeenHomed

    def AimPanTiltRel(self, panDegrees: float, tiltDegrees: float) -> None:
        '''Move motors relative in x and y'''
        xMove = self.threadPool.submit(self.panMotor.RotateRel, panDegrees)
        yMove = self.threadPool.submit(self.tiltMotor.RotateRel, tiltDegrees)
        
        for f in futures.as_completed([xMove, yMove]):
            f.result()
    
    def MoveMotorRel(self, motor: MotorEnum, degrees: float):
        match motor:
            case MotorEnum.Pan:
                self.panMotor.RotateRel(degrees)
            case MotorEnum.Tilt:
                self.tiltMotor.RotateRel(degrees)
            case _:
                print("Unknown motor")

    def MoveXRel(self, degrees: float) -> bool:
        madePosition = self.panMotor.RotateRel(degrees)
        return madePosition

    def MoveYRel(self, degrees: float) -> bool:
        madePosition = self.tiltMotor.RotateRel(degrees)
        return madePosition
    
    def MovePanAbs(self, degrees: float) -> bool:
        madePosition = self.panMotor.RotateAbs(degrees)
        return madePosition
    
    def MoveTiltAbs(self, degrees: float) -> bool:
        madePosition = self.tiltMotor.RotateAbs(degrees)
        return madePosition

    def EnableMotor(self, motor: MotorEnum):
        match motor:
            case MotorEnum.Pan:
                self.panMotor.enabled = True
            case MotorEnum.Tilt:
                self.tiltMotor.enabled = True
            case _:
                print("Unknown motor")

    def DisableMotor(self, motor: MotorEnum):
        match motor:
            case MotorEnum.Pan:
                self.panMotor.enabled = False
            case MotorEnum.Tilt:
                self.tiltMotor.enabled = False
            case _:
                print("Unknown motor")

    def Jog(self, speed: int, cw: bool, motor: MotorEnum):
        '''Start motor rotating at specified speed until timeout

            args: 
                speed: in mm/s (int)
                cw: should motor spin in clockwise direction (bool)
                motor: which motor to jog. 1=x, 2=y (int)
        '''
        if(motor == MotorEnum.Pan):
            self.panMotor.Jog(speed, cw)
        elif(motor == MotorEnum.Tilt):
            self.tiltMotor.Jog(speed, cw)
        else:
            print("Error: Invalid parameter received for 'motor' argument of AimingControl.Jog")

    def StopMotors(self):
        self.panMotor.Stop()
        self.tiltMotor.Stop()

    def SetTiltMotorLimits(self, limits: Tuple[float, float]):
        """
        Set cw and ccw limits for tilt motor in degrees

        Args:
            limits: position limits in degrees (CW limit, CCW limit)
        """
        self.tiltMotor.SetLimits(limits)

    def SetTiltMotorLimit(self, limit: float, isUpper: bool):
        """
        Set either upper or lower limit for tilt motor in degrees

        Args:
            limit: position limit in degrees
            isUpper: true if setting upper limit, false if setting lower limit
        """
        self.tiltMotor.SetLimit(limit, isUpper)

    def GetTiltLimits(self) -> Tuple[float, float]:
        '''Get tilt motor limits in degrees (cw limit, ccw limit)'''
        return self.tiltMotor.limits

    def SetHomeReference(self):
        '''Set current position of motors as home reference point (0,0)'''
        self.panMotor.SetHomeReference()
        self.tiltMotor.SetHomeReference()