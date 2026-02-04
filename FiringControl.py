from DCMotorControl import DCMotorControl
from AmmoControl import AmmoControl
from threading import Timer
from MotorEnums import MotorEnum
from ConfigClasses import SystemConfig
import threading
class FiringControl:
    def __init__(self, ammoControl: AmmoControl, spoolMotors: DCMotorControl, config: SystemConfig):
        self.ammoControl = ammoControl
        self.spoolMotors = spoolMotors
        self._config = config
        self.motorsSpooled = False
        self._motorsSpooledTimer = threading.Timer(self._config.spoolTime, self._MarkMotorsSpooled)
    
    @property
    def motorPositions(self) -> dict[MotorEnum, float]:
        pos = {}
        pos[MotorEnum.Chamber] = self.ammoControl.motorPositions[MotorEnum.Chamber]
        return pos

    def ChamberSingle(self):
        '''Load a single ammo unit into the chamber - will cause it to fire if motors spooled'''
        self.ammoControl.FireSingle()

    def SetChamberServoAngle(self, angle: float):
        self.ammoControl.SetChamberServoAngle(angle)
    
    def OpenChamberServo(self):
        self.ammoControl.OpenChamberServo()

    def CloseChamberServo(self):
        self.ammoControl.CloseChamberServo()

    def StopMotors(self):
        '''Stops spool motors'''
        self.spoolMotors.StopMotors()

    def SpoolMotors(self):
        '''Starts spooling motors. Once spooled, sets "motorsSpooled" true'''
        self.spoolMotors.SpoolMotors()
        self._RestartMotorsSpooledTimer()

    def SpoolMotorsWithTimeout(self):
        '''Spools motors and stops after timeout if another spool command isn't received'''
        self.SpoolMotors()
        self._RestartManSpoolTimer()
    
    def DisableMotor(self, motorNum: MotorEnum):
        match motorNum:
            case MotorEnum.Spool:
                self.spoolMotors.DisableMotor()
            case MotorEnum.Chamber:
                print("Enable/Disable of chamber motor not supported")
            case _:
                print("Unknown motor")

    def EnableMotor(self, motorNum: MotorEnum):
        match motorNum:
            case MotorEnum.Spool:
                self.spoolMotors.EnableMotor()
            case MotorEnum.Chamber:
                print("Enable/Disable of chamber motor not supported")
            case _:
                print("Unknown motor")

    def _RestartManSpoolTimer(self):
        '''Cancels current timeout timer if active and starts a new one for the timeout duration'''
        self._manSpoolTimer.cancel()
        self._manSpoolTimer = Timer(self._config.manualSpoolTimeout, self.StopMotors)
        self._manSpoolTimer.start()

    def _RestartMotorsSpooledTimer(self):
        '''Cancels current motors spooled timer if active and starts a new one for the min spool time'''
        self._motorsSpooledTimer.cancel()
        self._motorsSpooledTimer = Timer(self._config.spoolTime, self._MarkMotorsSpooled)
        self._motorsSpooledTimer.start()

    def _MarkMotorsSpooled(self): self.motorsSpooled = True
