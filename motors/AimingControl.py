from concurrent import futures
from typing import Tuple
from .StepperMotorControl import StepperMotorControl
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

    def MoveXRel(self, degrees: float):
        self.panMotor.RotateRel(degrees)

    def MoveYRel(self, degrees: float):
        self.tiltMotor.RotateRel(degrees)
    
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

   