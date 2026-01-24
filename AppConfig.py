from dataclasses import dataclass
from ConfigClasses import *
class AppConfig:    
    systemConfig: SystemConfig
    clientConfig: ClientConfig
    aimMotorsConfig: AimMotorsConfig
    firingMotorConfig: FiringMotorConfig
    cameraConfig: CameraConfig


    @classmethod
    def load_config(cls, directoryPath: str) -> "AppConfig":
        import json

        def load_file(filePath):
            with open(directoryPath + filePath, 'r') as f:
                data = json.load(f)

        systemData = load_file("system_config.json")
        clientData = load_file("client_config.json")
        aimMotorsData = load_file("aim_motors_config.json")
        firingMotorData = load_file("firing_motor_config.json")
        cameraData = load_file("camera_config.json")
        return cls(
            systemConfig=SystemConfig(**systemData),
            clientConfig=ClientConfig(**clientData),
            aimMotorsConfig=AimMotorsConfig(**aimMotorsData),
            firingMotorConfig=FiringMotorConfig(**firingMotorData),
            cameraConfig=CameraConfig(**cameraData)
        )