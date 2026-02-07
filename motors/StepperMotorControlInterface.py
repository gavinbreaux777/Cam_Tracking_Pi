from abc import ABC, abstractmethod

class StepperMotorControlInterface(ABC):
    @property
    @abstractmethod
    def speed(self, degreesPerSecond: int):
        pass

    @property
    @abstractmethod
    def accel(self, degreesPerSecondSquared: float):
        pass

    @abstractmethod
    def __init__(self, stepPin: int, dirPin: int = None, stepResPins: tuple[int, int, int] = None ):
        pass

    @abstractmethod
    def RotateRel(self, degrees: float):
        pass

    @abstractmethod
    def RotateAbs(self, targetDegrees: float):
        pass

    @abstractmethod
    def Stop(self):
        pass