from flask import Blueprint
from typing import Any
from camera.Detector import Detector
from config.ConfigClasses import CameraConfig, ImageProcessorConfig

def create_imageProcessing_blueprint(detector: "Detector", imageProcessorConfig: "ImageProcessorConfig", camConfig: "CameraConfig"):

    imageProcessing_bp = Blueprint('imageProcessing', __name__)

    @imageProcessing_bp.route('/stopImgMod')
    def stopImageModification():
        detector.processImage = False
        return "OkeY DoKEy", 200

    @imageProcessing_bp.route('/startImgMod')
    def startImageModification():
        detector.processImage = True
        return "OkeY DoKEy", 200
    
    @imageProcessing_bp.route('/toggleDelta/<show>')
    def toggleDelta(show):
        if(show == "true"):
            detector.showDelta = True
        else:
            detector.showDelta = False
        return "OKeY DOkeY", 200

    @imageProcessing_bp.route('/toggleContours/<show>')
    def toggleContours(show):
        if(show == "true"):
            detector.showContours = True
        else:
            detector.showContours = False
        return "OKeY DOkeY", 200
    
    @imageProcessing_bp.route('/modCamSetting/<settingName>/<settingValue>')
    def setCameraSetting(settingName: str, settingValue: Any):
        setattr(camConfig, settingName, settingValue)
        #detector.ModifyCameraSetting(settingName, settingValue)
        return "oKeY DoKEy thEN", 200
    
    @imageProcessing_bp.route('/modImgProcSetting/<settingName>/<settingValue>')
    def setImageProcessSetting(settingName: str, settingValue: Any):
        print("Settomg ma,e = "+ settingName)
        print("preval = "+ str(getattr(imageProcessorConfig, settingName)))
        setattr(imageProcessorConfig, settingName, settingValue)
        print(getattr(imageProcessorConfig, settingName))
        return "okey dokey then", 200
    
    return imageProcessing_bp
