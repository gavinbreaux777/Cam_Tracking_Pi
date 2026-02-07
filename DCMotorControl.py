from IOControl import IOControl
import threading
from ConfigClasses import FiringMotorConfig

class DCMotorControl:
    def __init__(self, ioControl: IOControl, config: FiringMotorConfig):
        self._ioControl = ioControl
        self._relayOnPin = config.onPin
        self._ioControl.SetPinMode(self._relayOnPin, 1)
        self._enabled = True

        self._manualSpoolTimeout = config.manSpoolTimeout
        self._manSpoolTimer = threading.Timer(self._manualSpoolTimeout, self.StopMotors)

        self._minSpoolTime = config.minSpoolTime
        self.motorsSpooled = False
        self._motorsSpooledTimer = threading.Timer(self._minSpoolTime, self._MarkMotorsSpooled)

    def SpoolMotors(self):
        '''Spins up dc motors. Sets property motorsSpooled to true after minSpoolTime has elapsed'''
        if(self._enabled == True):
            self._ioControl.SetOutput(self._relayOnPin, 1)
            
    def StopMotors(self):
        '''Stop dc motors'''
        self._ioControl.SetOutput(self._relayOnPin, 0)
        self._manSpoolTimer.cancel()
        self._motorsSpooledTimer.cancel()
        self.motorsSpooled = False    

    def DisableMotor(self):
        self._enabled = False
    
    def EnableMotor(self):
        self._enabled = True

    def _MarkMotorsSpooled(self):
        self.motorsSpooled = True