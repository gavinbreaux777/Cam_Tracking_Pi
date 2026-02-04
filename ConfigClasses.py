from dataclasses import dataclass
@dataclass
class SystemConfig():
    tiltDegreesPerCamPercentChange: float
    panDegreesPerCamPercentChange: float
    actOnDetection: bool
    spoolTime: float
    manualSpoolTimeout: float

@dataclass
class ClientConfig:
    pass

@dataclass
class MotorConfig:
    aimMotors: 'AimMotorsConfig'
    firingMotor: 'FiringMotorConfig'
    chamberServo: 'ChamberServoConfig'

@dataclass
class AimMotorsConfig:
    panMotor: 'SingleAimMotorConfig'
    tiltMotor: 'SingleAimMotorConfig'

@dataclass
class SingleAimMotorConfig:
    mock: bool = False
    stepPin: int = 0
    dirPin: int = 0
    enablePin: int = 0
    stepMode: str = "1"
    speed: int = 50,
    stepsPerRev: int = 200

@dataclass
class FiringMotorConfig:
    mock: bool = False
    onPin: int = 0
    minSpoolTime: float = 0.2
    manSpoolTimeout: float = 1.0

@dataclass
class ChamberServoConfig:
    mock: bool = False
    pwmPin: int = 0
    openAngle: float = 0.0
    closedAngle: float = 0.0
    pulseFrequency: float = 50.0

@dataclass
class IOConfig:
    mock: bool = False

@dataclass
class CameraConfig:
    mock: bool = False
    imgSize: tuple[int, int] = (640,480)

@dataclass
class ImageProcessorConfig:
    pass