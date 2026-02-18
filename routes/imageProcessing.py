from flask import Blueprint
from typing import Any
from camera.ProcessImage import ProcessImage
from camera.Detector import Detector
from LoggerSetup import LoggerSetup, log_user_action

logger = LoggerSetup.get_logger("ImageProcessingRoutes")

def create_imageProcessing_blueprint(detector: "Detector", imageProcessor: "ProcessImage"):

    imageProcessing_bp = Blueprint('imageProcessing', __name__)

    @imageProcessing_bp.route('/stopImgMod')
    @log_user_action("User stopped image processing")
    def stopImageModification():
        logger.info("Stopping image modification/processing")
        detector.processImage = False
        return "OkeY DoKEy", 200

    @imageProcessing_bp.route('/startImgMod')
    @log_user_action("User started image processing")
    def startImageModification():
        logger.info("Starting image modification/processing")
        detector.processImage = True
        return "OkeY DoKEy", 200
    
    @imageProcessing_bp.route('/modImgProcSetting/<settingName>/<settingValue>')
    @log_user_action("User modified image processing setting")
    def setImageProcessSetting(settingName: str, settingValue: Any):
        try:
            setattr(imageProcessor.config, settingName, settingValue)
            logger.info(f"Image processing setting changed: {settingName} = {settingValue}")
            return "okey dokey then", 200
        except Exception as e:
            logger.error(f"Error setting image processing setting {settingName}: {e}", exc_info=True)
            return "Error", 500

    @imageProcessing_bp.route('/toggleDelta/<show>')
    @log_user_action("User toggled delta visualization")
    def toggleDelta(show):
        if(show == "true"):
            detector.showDelta = True
            logger.info("Delta visualization ENABLED")
        else:
            detector.showDelta = False
            logger.info("Delta visualization DISABLED")
        return "OKeY DOkeY", 200

    @imageProcessing_bp.route('/toggleContours/<show>')
    @log_user_action("User toggled contours visualization")
    def toggleContours(show):
        if(show == "true"):
            detector.showContours = True
            logger.info("Contours visualization ENABLED")
        else:
            detector.showContours = False
            logger.info("Contours visualization DISABLED")
        return "OKeY DOkeY", 200
    
    @imageProcessing_bp.route('/modCamSetting/<settingName>/<settingValue>')
    @log_user_action("User modified camera setting")
    def setCameraSetting(settingName: str, settingValue: Any):
        try:
            detector.ModifyCameraSetting(settingName, settingValue)
            logger.info(f"Camera setting changed: {settingName} = {settingValue}")
            return "oKeY DoKEy thEN", 200
        except Exception as e:
            logger.error(f"Error setting camera setting {settingName}: {e}", exc_info=True)
            return "Error", 500
    
    return imageProcessing_bp