#import RPi.GPIO as gpio
import time
from RawServoControl import RawServoControl
from IOControl import IOControl

class FiringControl():
    def __init__(self, ioControl: IOControl):
        self._ioControl = ioControl
        self.relayOnPin = 21
        self._ioControl.SetPinMode(self.relayOnPin, 1)

        self.servo = RawServoControl(ioControl, 12, 50)
        self.closedAngle = 165
        self.openAngle = 160
        self.servo.SetAngle(self.closedAngle)

    @property
    def servoPosition(self) -> float:
        return self.servo.position

    def SpoolMotors(self):
        '''Spins up dc motors'''
        self._ioControl.SetOutput(self.relayOnPin, 1)

    def StopMotors(self):
        '''Stop dc motors'''
        self._ioControl.SetOutput(self.relayOnPin, 0)

    def FireSingle(self):
        '''Release single ball. Motors should be spooled already'''
        self.servo.SetAngle(self.openAngle)
        time.sleep(0.1) #Add sensor to allow only 1 ball?
        self.servo.SetAngle(self.closedAngle) 

    def OpenGate(self):
        '''Open gate to release all balls'''
        self.servo.SetAngle(self.openAngle)

    def CloseGate(self):
        '''Close gate to stop releasing balls'''
        self.servo.SetAngle(self.closedAngle)

    def SetServoAngle(self, angle: float):
        self.servo.SetAngle(angle)