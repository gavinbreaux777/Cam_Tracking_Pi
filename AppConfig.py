from ConfigClasses import *
import json
from dacite import from_dict
class AppConfig:    
    systemConfig: SystemConfig
    clientConfig: ClientConfig
    cameraConfig: CameraConfig
    motorConfig: MotorConfig
    ioConfig: IOConfig

    def __init__(self, directoryPath: str):
        self.directoryPath = directoryPath
        systemConfigData = self.load_file("SystemConfig.json")        
        clientConfigData = self.load_file("ClientConfig.json")
        motorsConfigData = self.load_file("MotorsConfig.json")
        cameraConfigData = self.load_file("CameraConfig.json")
        ioConfigData = self.load_file("IOConfig.json")
        imageProcessorConfigData = self.load_file("ImageProcessorConfig.json")

        self.systemConfig = from_dict(SystemConfig, systemConfigData)
        self.clientConfig = from_dict(ClientConfig, clientConfigData)
        self.cameraConfig = from_dict(CameraConfig, cameraConfigData)
        self.motorConfig = from_dict(MotorConfig, motorsConfigData)
        self.ioConfig = from_dict(IOConfig, ioConfigData)
        self.imageProcessorConfig = from_dict(ImageProcessorConfig, imageProcessorConfigData)

    def load_file(self, filePath):
            with open(self.directoryPath + filePath, 'r') as f:
                return json.load(f)
            