from flask import Blueprint
from motors.MotorEnums import MotorEnum
from motors.MotorControl import MotorControl
from config.ConfigClasses import MotorConfig
from LoggerSetup import LoggerSetup, log_user_action

logger = LoggerSetup.get_logger("MotorsRoutes")

def create_motors_blueprint(motorControl: "MotorControl", motorConfig: "MotorConfig"):

    motors_bp = Blueprint('motors', __name__)

    @motors_bp.route('/motorControl/<direction>/<speed>')
    @log_user_action("User jogged motor")
    def jogMotor(direction: str, speed: str):
        speedInt = int(speed)
        match direction:
            case "left":
                logger.info(f"Jogging Pan motor LEFT at speed {speedInt}")
                motorControl.JogMotor(MotorEnum.Pan, speedInt, True)
            case "right":
                logger.info(f"Jogging Pan motor RIGHT at speed {speedInt}")
                motorControl.JogMotor(MotorEnum.Pan, speedInt, False)
            case "up":
                logger.info(f"Jogging Tilt motor UP at speed {speedInt}")
                motorControl.JogMotor(MotorEnum.Tilt, speedInt, True)
            case "down":
                logger.info(f"Jogging Tilt motor DOWN at speed {speedInt}")
                motorControl.JogMotor(MotorEnum.Tilt, speedInt, False)
            case _:
                logger.error(f"Invalid direction parameter received: {direction}")
                return "Invalid direction parameter", 400
        return "Okey Dokey", 200

    @motors_bp.route('/stopAimMotors')
    @log_user_action("User stopped aim motors")
    def stopAimMotors():
        logger.info("Stopping Pan and Tilt motors")
        motorControl.StopMotor(MotorEnum.Pan)
        motorControl.StopMotor(MotorEnum.Tilt)
        return "okeY DokeY", 200

    @motors_bp.route('/openChamberServo')
    @log_user_action("User opened chamber servo")
    def openChamberServo():
        logger.info("Opening chamber servo")
        motorControl.OpenChamberServo()
        return "okeY DOkey", 200

    @motors_bp.route('/closeChamberServo')
    @log_user_action("User closed chamber servo")
    def closeChamberServo():
        logger.info("Closing chamber servo")
        motorControl.CloseChamberServo()
        return "okeY DOkey", 200

    @motors_bp.route('/teachServo/<state>')
    @log_user_action("User taught servo position")
    def teachServo(state: str):
        """Record the current chamber servo position as taught open/closed."""
        try:
            current_pos = motorControl.GetMotorPos(MotorEnum.Chamber)
            if state == 'open':
                motorConfig.chamberServo.openAngle = current_pos
                logger.info(f"Taught servo open position: {current_pos}")
            elif state == 'closed':
                motorConfig.chamberServo.closedAngle = current_pos
                logger.info(f"Taught servo closed position: {current_pos}")
            else:
                logger.error(f"Unknown servo state: {state}")
                return f"Unknown state: {state}", 400
            return "OK", 200
        except Exception as e:
            logger.error(f"Error in teachServo: {e}", exc_info=True)
            return "Error", 500
        
    @motors_bp.route('/moveChamberServo/<angle>')
    @log_user_action("User moved chamber servo")
    def moveChamberServo(angle: str):
        angleInt = float(angle)
        logger.info(f"Moving chamber servo to angle: {angleInt}")
        motorControl.MoveMotorAbs(MotorEnum.Chamber, angleInt)
        return "okeY DOkey", 200

    @motors_bp.route('/enableDisableMotor/<motorStr>/<clicked>')
    @log_user_action("User toggled motor enable/disable")
    def enableDisableMotor(motorStr: str, clicked: str):
        match motorStr:
            case "Pan":
                if(clicked == "true"):
                    logger.info("Enabling Pan motor")
                    motorControl.EnableMotor(MotorEnum.Pan)
                else:
                    logger.info("Disabling Pan motor")
                    motorControl.DisableMotor(MotorEnum.Pan)
            case "Tilt":
                if(clicked == "true"):
                    logger.info("Enabling Tilt motor")
                    motorControl.EnableMotor(MotorEnum.Tilt)
                else:
                    logger.info("Disabling Tilt motor")
                    motorControl.DisableMotor(MotorEnum.Tilt)
            case "Spool":
                if(clicked == "true"):
                    logger.info("Enabling Spool motor")
                    motorControl.EnableMotor(MotorEnum.Spool)
                else:
                    logger.info("Disabling Spool motor")
                    motorControl.DisableMotor(MotorEnum.Spool)
            case _:
                logger.error(f"Unknown motor: {motorStr}")
                return "Unknown motor: " + motorStr, 400
        return "Okey Dokey", 200

    @motors_bp.route('/spoolDCMotors')
    @log_user_action("User spooled DC firing motors")
    def spoolDCMotors():
        logger.info("Spooling firing motors")
        motorControl.SpoolFiringMotors()
        return "oKEY dokEY", 200

    @motors_bp.route('/stopDCMotors')
    @log_user_action("User stopped DC motors")
    def stopDCMotors():
        logger.info("Stopping DC spool motor")
        motorControl.StopMotor(MotorEnum.Spool)
        return "OKeY DOKey", 200

    @motors_bp.route('/calibrateMotors/<xDegreesToPercentChange>/<yDegreesToPercentChange>')
    @log_user_action("User calibrated motors")
    def CalibrateMotors(xDegreesToPercentChange: float, yDegreesToPercentChange: float):
        x_val = float(xDegreesToPercentChange)
        y_val = float(yDegreesToPercentChange)
        motorConfig.aimMotors.panMotor = x_val
        motorConfig.aimMotors.tiltMotor = y_val
        logger.info(f"Calibrated motors - Pan: {x_val} deg/%, Tilt: {y_val} deg/%")
        return "Okey Dokey", 200

    @motors_bp.route('/setTiltLimit/<limit>/<value>')
    @log_user_action("User set tilt limit")
    def SetTiltLimit(limit: str, value: str):
        try:
            valueInt = float(value)
        except(ValueError):
            logger.error(f"Invalid tilt limit value: {value}")
            return "Invalid value parameter", 400
        match limit:
            case "upper":
                logger.info(f"Setting upper tilt limit to {valueInt}")
                motorControl.SetTiltLimit(valueInt, True)
            case "lower":
                logger.info(f"Setting lower tilt limit to {valueInt}")
                motorControl.SetTiltLimit(valueInt, False)
            case _:
                logger.error(f"Invalid tilt limit parameter: {limit}")
                return "Invalid limit parameter", 400
        return "OK", 200
    
    @motors_bp.route('/setAimMotorsHome')
    @log_user_action("User set aim motors home reference")
    def SetAimMotorsHome():
        logger.info("Setting aim motors home reference")
        motorControl.SetHomeReference()
        return "OK", 200
    
    @motors_bp.route('/moveAimMotorsHome')
    @log_user_action("User moved aim motors to home")
    def MoveAimMotorsHome():
        logger.info("Moving aim motors to home position (0, 0)")
        motorControl.MoveMotorAbs(MotorEnum.Pan, 0)
        motorControl.MoveMotorAbs(MotorEnum.Tilt, 0)
        return "OK", 200

    return motors_bp