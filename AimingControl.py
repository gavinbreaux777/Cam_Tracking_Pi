from StepperMotorControl import StepperMotorControl
from concurrent import futures

class AimingControl():
    def __init__(self):
        self.xMotor = StepperMotorControl(18) 
        self.yMotor = StepperMotorControl(17)

    @property
    def motorSpeed(self) ->tuple[float, float]: 
        '''Speed for both motors in degPerSec'''
        return tuple[self.xMotor.speed, self.yMotor.speed]
    
    @motorSpeed.setter
    def motorSpeed(self, xSpeed: float, ySpeed: float):
        self.xMotor.speed(xSpeed)
        self.yMotor.speed(ySpeed)


    def AimXYRel(self, xDegrees: float, yDegrees: float):
        '''Move motors relative in x and y'''
        threadPool = futures.ThreadPoolExecutor()
        xMove = threadPool.submit(self.xMotor.RotateRel, xDegrees)
        yMove = threadPool.submit(self.yMotor.RotateRel,yDegrees)
        futures.wait([xMove, yMove])
    
    def MoveXRel(self, degrees: float):
        self.xMotor.RotateRel(degrees)

    def MoveYRel(self, degrees: float):
        self.yMotor.RotateRel(degrees)