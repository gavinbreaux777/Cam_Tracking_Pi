from dataclasses import dataclass
@dataclass
class SystemConfig:
    pass

@dataclass
class ClientConfig:
    pass

@dataclass
class MotorConfig:
    aimMotorsConfig: 'AimMotorsConfig'
    firingMotorConfig: 'FiringMotorConfig'
    ChamberServoConfig: 'ChamberServoConfig'

@dataclass
class AimMotorsConfig:
    panMotor: 'SingleAimMotorConfig'
    tiltMotor: 'SingleAimMotorConfig'

@dataclass
class SingleAimMotorConfig:
    mockMode: bool = False
    stepPin: int = 0
    dirPin: int = 0
    enablePin: int = 0
    stepMode: str = "1"

@dataclass
class FiringMotorConfig:
    mockMode: bool = False

@dataclass
class ChamberServoConfig:
    mockMode: bool = False

@dataclass
class CameraConfig:
    mockMode: bool = False