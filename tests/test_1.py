import pytest
from unittest.mock import Mock
from FlaskServer import FlaskServer


@pytest.fixture
def mock_detector():
    """Create a mock Detector object."""
    detector = Mock()
    detector.output = Mock()
    detector._imgProcessor = Mock()
    detector._imgProcessor._baseImg = Mock()
    detector._imgProcessor.detectImg = Mock()
    detector.processImage = True
    detector.showDelta = False
    detector.showContours = False
    return detector


@pytest.fixture
def mock_motor_control():
    """Create a mock MotorControl object."""
    motor_control = Mock()
    motor_control.motionStartedEvent = Mock()
    motor_control.motionEndedEvent = Mock()
    motor_control.motionStartedEvent.Subscribe = Mock()
    motor_control.motionEndedEvent.Subscribe = Mock()
    return motor_control

@pytest.fixture
def mock_config():
    """Create a mock config object."""
    config = Mock()
    return config

@pytest.fixture
def flask_app(mock_detector, mock_motor_control, mock_config):
    """Create a Flask test client."""
    flask_server = FlaskServer(mock_detector, mock_motor_control, mock_config)
    flask_server.app.config['TESTING'] = True
    return flask_server.app.test_client()


class TestFlaskServerLaunch:
    """Test that Flask server launches and responds correctly."""

ROUTES = [
    ('/', None),
    ('/stream', None),
    ('/base-img', None),
    ('/detect-img', None),
    ('/stopStream', None),
    ('/stopImgMod', None),
    ('/startImgMod', None),
    ('/dataEventSoruce', None),
    ('/detectNotifySource', None),
    ('/motorControl/{direction}/{speed}', {'direction': 'left', 'speed': 10}),
    ('/stopAimMotors', None),
    ('/modImgProcSetting/{settingName}/{settingValue}', {'settingName': 'brightness', 'settingValue': 50}),
    ('/modCamSetting/{settingName}/{settingValue}', {'settingName': 'exposure', 'settingValue': 100}),
    ('/motorLocation', None),
    ('/calibrateMotors/{xDegreesToPercentChange}/{yDegreesToPercentChange}', {'xDegreesToPercentChange': 5, 'yDegreesToPercentChange': 10}),
    ('/moveChamberServo/{angle}', {'angle': 90}),
    ('/openChamberServo', None),
    ('/closeChamberServo', None),
    ('/teachServo/{state}', {'state': 'open'}),
    ('/forceDetection/{xRatio}/{yRatio}', {'xRatio': 0.5, 'yRatio': 0.7}),
    ('/toggleDelta/{show}', {'show': 'true'}),
    ('/toggleContours/{show}', {'show': 'false'}),
    ('/enableDisableMotor/{motorStr}/{clicked}', {'motorStr': 'Pan', 'clicked': 1}),
    ('/enableDisableDCMotor/{clicked}', {'clicked': 1}),
    ('/spoolDCMotors', None),
    ('/stopDCMotors', None),
    ('/actOnDetection/{onOff}', {'onOff': 'on'}),
]

# Skip streaming/SSE routes in tests
SKIP_ROUTES = ['/stream', '/dataEventSoruce', '/detectNotifySource', '/motorLocation']

@pytest.mark.parametrize("route,params", ROUTES)
def test_routes_return_200(flask_app, route, params):
    """Test all non-streaming routes return 200 with example parameters."""
    if route in SKIP_ROUTES:
        pytest.skip(f"Skipping route: {route}")

    formatted = route.format(**params) if params else route
    print(f"Testing route: {formatted}")
    response = flask_app.get(formatted)
    assert response.status_code == 200