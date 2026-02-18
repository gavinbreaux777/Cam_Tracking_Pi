from ClassFactory import ClassFactory
from config.AppConfig import AppConfig

from FlaskServer import FlaskServer
from camera.Detector import Detector
from i_o.IOControl import IOControl
from LoggerSetup import LoggerSetup

# Initialize logger for the application
logger = LoggerSetup.get_logger("Main")

#load config values
logger.info("Loading application configuration...")
config = AppConfig("config/")
logger.info("Configuration loaded successfully")

#Create class to handle camera and image processing
logger.info("Initializing camera...")
picam2 = ClassFactory.ReturnCamera(config.cameraConfig)
detector = Detector(picam2)
logger.info("Camera initialized")

#Create class to handle IO
logger.info("Initializing IO control...")
io = ClassFactory.ReturnIO(config.ioConfig)
ioControl = IOControl(io)
logger.info("IO control initialized")

#Create class to control all motors, aiming and projection
logger.info("Initializing motor control...")
motorControl = ClassFactory.ReturnMotorControl(ioControl, config.motorConfig, config.systemConfig)
logger.info("Motor control initialized")

try:
    #code start
    logger.info("=" * 60)
    logger.info("STARTING CAM TRACKING PI APPLICATION")
    logger.info("=" * 60)
    
    #Start the camera recording
    logger.info("Starting camera recording...")
    detector.StartRecording()
    logger.info("Camera recording started")
    
    #start Flask server with output from camera recording
    logger.info("Starting Flask server...")
    server = FlaskServer(detector, motorControl, config)

    detector.RegisterObserver(motorControl)
    detector.RegisterObserver(server)
    logger.info("Observers registered")
    
    server.startServer()

except Exception as e:
    logger.error(f"Application error: {type(e).__name__}: {str(e)}", exc_info=True)
    raise
finally:
    logger.info("Stopping camera recording...")
    detector.StopRecording()
    logger.info("=" * 60)
    logger.info("CAMERA TRACKING PI APPLICATION STOPPED")
    logger.info("=" * 60)

