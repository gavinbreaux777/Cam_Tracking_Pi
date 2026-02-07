from flask import Blueprint
from motors.MotorEnums import MotorEnum
from motors.MotorControl import MotorControl
from config.ConfigClasses import MotorConfig

def create_motors_blueprint(motorControl: "MotorControl", motorConfig: "MotorConfig"):

    motors_bp = Blueprint('motors', __name__)

    @motors_bp.route('/motorControl/<direction>/<speed>')
    def jogMotor(direction: str, speed: str):
        speedInt = int(speed)
        match direction:
            case "left":
                motorControl.JogMotor(MotorEnum.Pan, speedInt, True)
            case "right":
                motorControl.JogMotor(MotorEnum.Pan, speedInt, False)
            case "up":
                motorControl.JogMotor(MotorEnum.Tilt, speedInt, True)
            case "down":
                motorControl.JogMotor(MotorEnum.Tilt, speedInt, False)
            case _:
                print("Invalid direction parameter received: " + direction)
                return "Invalid direction parameter", 400
        return "Okey Dokey", 200

    @motors_bp.route('/stopAimMotors')
    def stopAimMotors():
        motorControl.StopMotor(MotorEnum.Pan)
        motorControl.StopMotor(MotorEnum.Tilt)
        return "okeY DokeY", 200

    @motors_bp.route('/openChamberServo')
    def openChamberServo():
        print("opening servo")
        motorControl.OpenChamberServo()
        return "okeY DOkey", 200

    @motors_bp.route('/closeChamberServo')
    def closeChamberServo():
        print("closing servo")
        motorControl.CloseChamberServo()
        return "okeY DOkey", 200

    @motors_bp.route('/teachServo/<state>')
    def teachServo(state: str):
        """Record the current chamber servo position as taught open/closed."""
        try:
            current_pos = motorControl.GetMotorPos(MotorEnum.Chamber)
            if state == 'open':
                motorConfig.chamberServo.openAngle = current_pos
            elif state == 'closed':
                motorConfig.chamberServo.closedAngle = current_pos
            else:
                return f"Unknown state: {state}", 400
            return "OK", 200
        except Exception as e:
            print(f"Error in teachServo: {e}")
            return "Error", 500
        
    @motors_bp.route('/moveChamberServo/<angle>')
    def moveChamberServo(angle: str):
        angleInt = float(angle)
        print("moving servo")
        motorControl.MoveMotor(MotorEnum.Chamber, angleInt)
        return "okeY DOkey", 200

    @motors_bp.route('/enableDisableMotor/<motorStr>/<clicked>')
    def enableDisableMotor(motorStr: str, clicked: str):
        match motorStr:
            case "Pan":
                if(clicked == "true"):
                    motorControl.EnableMotor(MotorEnum.Pan)
                else:
                    motorControl.DisableMotor(MotorEnum.Pan)
            case "Tilt":
                if(clicked == "true"):
                    motorControl.EnableMotor(MotorEnum.Tilt)
                else:
                    motorControl.DisableMotor(MotorEnum.Tilt)
            case "Spool":
                if(clicked == "true"):
                    motorControl.EnableMotor(MotorEnum.Spool)
                else:
                    motorControl.DisableMotor(MotorEnum.Spool)
            case _:
                print("Unknown motor: " + motorStr)
                return "Unknown motor: " + motorStr, 400
        return "Okey Dokey", 200

    @motors_bp.route('/spoolDCMotors')
    def spoolDCMotors():
        motorControl.SpoolFiringMotors()
        return "oKEY dokEY", 200

    @motors_bp.route('/stopDCMotors')
    def stopDCMotors():
        motorControl.StopMotor(MotorEnum.Spool)
        return "OKeY DOKey", 200

    @motors_bp.route('/calibrateMotors/<xDegreesToPercentChange>/<yDegreesToPercentChange>')
    def CalibrateMotors(xDegreesToPercentChange: float, yDegreesToPercentChange: float):
        motorConfig.aimMotors.panMotor = float(xDegreesToPercentChange)
        motorConfig.aimMotors.tiltMotor = float(yDegreesToPercentChange)
        print(str(xDegreesToPercentChange) + " , " + str(yDegreesToPercentChange))
        return "Okey Dokey", 200
    
    return motors_bp