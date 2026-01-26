from IOControl import IOControl
import threading
from ConfigClasses import FiringMotorConfig

class DCMotorControl:
    def __init__(self, ioControl: IOControl, config: FiringMotorConfig):
        self._ioControl = ioControl
        self.relayOnPin = config.onPin
        self._ioControl.SetPinMode(self.relayOnPin, 1)
        self.enabled = True

        self.manualSpoolTimeout = config.manSpoolTimeout
        self._manSpoolTimer = threading.Timer(self.manualSpoolTimeout, self.StopMotors)

        self.minSpoolTime = config.minSpoolTime
        self.motorsSpooled = False
        self._motorsSpooledTimer = threading.Timer(self.minSpoolTime, self._MarkMotorsSpooled)

    def SpoolMotors(self):
        '''Spins up dc motors. Sets property motorsSpooled to true after minSpoolTime has elapsed'''
        if(self.enabled == True):
            self._ioControl.SetOutput(self.relayOnPin, 1)
            self._RestartMotorsSpooledTimer()
    
    def SpoolMotorsWithTimeout(self):
        '''Spools motors and stops after timeout if another spool command isn't received'''
        self.SpoolMotors()
        self._RestartManSpoolTimer()

    def _RestartManSpoolTimer(self):
        '''Cancels current timeout timer if active and starts a new one for the timeout duration'''
        self._manSpoolTimer.cancel()
        self._manSpoolTimer = threading.Timer(self.manualSpoolTimeout, self.StopMotors)
        self._manSpoolTimer.start()

    def StopMotors(self):
        '''Stop dc motors'''
        self._ioControl.SetOutput(self.relayOnPin, 0)
        self._manSpoolTimer.cancel()
        self._motorsSpooledTimer.cancel()
        self.motorsSpooled = False
    

    def _RestartMotorsSpooledTimer(self):
        '''Cancels current motors spooled timer if active and starts a new one for the min spool time'''
        self._motorsSpooledTimer.cancel()
        self._motorsSpooledTimer = threading.Timer(self.minSpoolTime, self._MarkMotorsSpooled)
        self._motorsSpooledTimer.start()

    def _MarkMotorsSpooled(self): self.motorsSpooled = True