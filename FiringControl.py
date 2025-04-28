import time
from RawServoControl import RawServoControl
from IOControl import IOControl
import threading

class FiringControl():
    def __init__(self, ioControl: IOControl):
        self._ioControl = ioControl
        self.relayOnPin = 21
        self._ioControl.SetPinMode(self.relayOnPin, 1)
        self.enabled = True
        self.manualSpoolTimeout = 100
        self._spoolTimer = threading.Timer(self.manualSpoolTimeout, self.StopMotors)


        self.servo = RawServoControl(ioControl, 12, 50)
        self.closedAngle = 160
        self.openAngle = 155
        self.servo.SetAngle(self.closedAngle)

    @property
    def servoPosition(self) -> float:
        return self.servo.position

    def SpoolMotors(self):
        '''Spins up dc motors'''
        if(self.enabled == True):
            self._ioControl.SetOutput(self.relayOnPin, 1)

    def SpoolMotorsWithTimeout(self):
        '''Spools motors and stops after timeout if another spool command isn't received'''
        self.SpoolMotors()
        self.RestartSpoolTimer()

    def RestartSpoolTimer(self):
        '''Cancels current timeout timer if active and starts a new one for the timeout duration'''
        self._spoolTimer.cancel()
        self._spoolTimer = threading.Timer(self.manualSpoolTimeout, self.StopMotors)
        self._spoolTimer.start()

    def StopMotors(self):
        '''Stop dc motors'''
        self._ioControl.SetOutput(self.relayOnPin, 0)
        self._spoolTimer.cancel()

    def FireSingle(self):
        '''Release single ball. Motors should be spooled already'''
        if(self.enabled == True):
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