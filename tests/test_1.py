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
def flask_app(mock_detector, mock_motor_control):
    """Create a Flask test client."""
    flask_server = FlaskServer(mock_detector, mock_motor_control)
    flask_server.app.config['TESTING'] = True
    return flask_server.app.test_client()


class TestFlaskServerLaunch:
    """Test that Flask server launches and responds correctly."""

    def test_server_initializes(self, mock_detector, mock_motor_control):
        """Test that Flask server initializes without errors."""
        server = FlaskServer(mock_detector, mock_motor_control)
        assert server.app is not None
        assert server.detector is mock_detector
        assert server.motorControl is mock_motor_control

    def test_home_route_returns_200(self, flask_app):
        """Test that home route returns 200 status code."""
        response = flask_app.get('/')
        assert response.status_code == 200

    def test_stop_stream_returns_200(self, flask_app):
        """Test that /stopStream endpoint returns 200 status code."""
        response = flask_app.get('/stopStream')
        assert response.status_code == 200
        assert b"OkeY DoKEy" in response.data

    def test_stop_image_modification_returns_200(self, flask_app):
        """Test that /stopImgMod endpoint returns 200 status code."""
        response = flask_app.get('/stopImgMod')
        assert response.status_code == 200
        assert b"OkeY DoKEy" in response.data

    def test_start_image_modification_returns_200(self, flask_app):
        """Test that /startImgMod endpoint returns 200 status code."""
        response = flask_app.get('/startImgMod')
        assert response.status_code == 200
        assert b"OkeY DoKEy" in response.data

    def test_motor_control_route_returns_200(self, flask_app):
        """Test that motor control endpoints return 200 status code."""
        response = flask_app.get('/motorControl/left/50')
        assert response.status_code == 200
        assert b"Okey Dokey" in response.data

    def test_stop_motors_returns_200(self, flask_app):
        """Test that /stopMotors endpoint returns 200 status code."""
        response = flask_app.get('/stopMotors')
        assert response.status_code == 200