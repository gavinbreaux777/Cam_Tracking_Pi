from StepperMotorControl import StepperMotorControl
from concurrent import futures
from typing import Tuple
from StepMode import StepMode
from IOControl import IOControl

class AimingControl():
    def __init__(self, ioControl: IOControl):
        self.xMotor = StepperMotorControl(ioControl, 18, 17, 19, StepMode.Sixteenth)
        self.yMotor = StepperMotorControl(ioControl, 23, 22, 24, StepMode.Sixteenth)

    @property
    def yPosition(self) -> float:
        return self.yMotor.position
    
    @property
    def xPosition(self) -> float:
        return self.xMotor.position

    @property
    def motorSpeed(self) ->Tuple[float, float]: 
        '''Speed for both motors in degPerSec'''
        return tuple[self.xMotor.speed, self.yMotor.speed]
    
    @motorSpeed.setter
    def motorSpeed(self, xySpeeds: Tuple[float, float]):
        self.xMotor.speed = xySpeeds[0]
        self.yMotor.speed = xySpeeds[1]

    def AimXYRel(self, xDegrees: float, yDegrees: float):
        '''Move motors relative in x and y'''
        threadPool = futures.ThreadPoolExecutor()
        xMove = threadPool.submit(self.xMotor.RotateRel, xDegrees)
        yMove = threadPool.submit(self.yMotor.RotateRel, yDegrees)
        futures.wait([xMove, yMove])
    
    def MoveXRel(self, degrees: float):
        self.xMotor.RotateRel(degrees)

    def MoveYRel(self, degrees: float):
        self.yMotor.RotateRel(degrees)

    def JogX(self, speed: int, cw: bool):
        self.xMotor.Jog(speed, cw) #Start motor rotating more than we will during jog, we will stop it via stop command
        
    def JogY(self, speed: int, cw: bool):
        self.yMotor.Jog(speed, cw)

    def Jog(self, speed: int, cw: bool, motor: int):
        '''Start motor rotating at specified speed until timeout

            args: 
                speed: in mm/s (int)
                cw: should motor spin in clockwise direction (bool)
                motor: which motor to jog. 1=x, 2=y (int)
        '''
        if(motor == 1):
            self.xMotor.Jog(speed, cw)
        elif(motor == 2):
            self.yMotor.Jog(speed, cw)
        else:
            print("Error: Invalid parameter received for 'motor' argument of AimingControl.Jog")

    def StopMotors(self):
        self.xMotor.Stop()
        self.yMotor.Stop()