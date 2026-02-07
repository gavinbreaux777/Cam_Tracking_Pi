from config.AppConfig import *
from unittest.mock import MagicMock
from camera.CameraInterface import CameraInterface

class ClassFactory():
    def __init__(self):
        pass

    @staticmethod
    def ReturnCamera(config: CameraConfig):        
        from CameraInterface import CameraInterface
        if(config.mock):
            import numpy as np
            mock_camera = MagicMock()
            mock_camera.Picamera2.capture_array.return_value = np.zeros((480, 640, 3), dtype=np.uint8) 
            
            return mock_camera
        else:
            import picamera2
            picamFromLib = picamera2
            cameraInterfacePicam = CameraInterface()
            cameraInterfacePicam.Picamera2 = picamFromLib.Picamera2()
            cameraInterfacePicam.encoders = picamera2.encoders
            cameraInterfacePicam.outputs = picamera2.outputs
            cameraInterfacePicam.Picamera2.MappedArray = picamFromLib.MappedArray
            cameraInterfacePicam.imgSize = config.imgSize
            return cameraInterfacePicam

    @staticmethod
    def ReturnIO(config: IOConfig):
        if(config.mock):
            return MagicMock()
        else:
            import pigpio
            return pigpio.pi()
        
    @staticmethod
    def ReturnMotorControl(ioControl, motorConfig: MotorConfig, systemConfig: SystemConfig):
        from motors.MotorControl import MotorControl
        from AimingControl import AimingControl
        from DCMotorControl import DCMotorControl
        from RawServoControl import RawServoControl
        from StepperMotorControl import StepperMotorControl
        from FiringControl import FiringControl
        from AmmoControl import AmmoControl

        #initialize individual motor classes and then pass to MotorControl
        panMotor = StepperMotorControl(ioControl, motorConfig.aimMotors.panMotor)
        tiltMotor = StepperMotorControl(ioControl, motorConfig.aimMotors.tiltMotor)
        aimingControl = AimingControl(panMotor, tiltMotor)

        chamberServo = RawServoControl(ioControl, motorConfig.chamberServo)
        ammoControl = AmmoControl(chamberServo)
        spoolMotors = DCMotorControl(ioControl, motorConfig.firingMotor)
        firingControl = FiringControl(ammoControl, spoolMotors, systemConfig)

        motorControl = MotorControl(aimingControl, firingControl, systemConfig)
        return motorControl

        if(motorConfig.aimMotors.panMotor.mock or
           motorConfig.aimMotors.tiltMotor.mock or 
           motorConfig.firingMotor.mock or 
           motorConfig.chamberServo.mock):
            raise Exception("Individual motor mocking not supported yet - use IO mocking instead to mock all motors")
        else:
            return MotorControl(ioControl, motorConfig)