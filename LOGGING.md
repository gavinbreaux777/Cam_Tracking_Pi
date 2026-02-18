# Logging Documentation

## Overview

A comprehensive logging system has been implemented throughout the Cam Tracking Pi project to track all user interactions and function calls in an easily reviewable format.

## Log Files Location

All logs are stored in the `logs/` directory at the project root:
```
logs/
├── cam_tracking_20260214.log  (daily log file)
└── cam_tracking_20260213.log  (previous days)
```

Log files are automatically rotated when they exceed 10 MB, with up to 5 backup files maintained.

## Log Levels

The logging system uses standard Python logging levels:

- **DEBUG**: Detailed diagnostic information (low-level function calls, state changes)
  - *Example*: "→ ENTER: MovePanAbs(0.5)" or "← EXIT: MovePanAbs() returned NoneType"
  
- **INFO**: General informational messages (user actions, important state changes)
  - *Example*: "◆ USER ACTION: User started camera stream" or "Motion detected at location X=10, Y=-5"
  
- **WARNING**: Warning messages for potential issues
  
- **ERROR**: Error messages and exceptions
  - *Example*: "✗ ERROR in StartRecording: RuntimeError: Camera initialization failed"

## Log Format

### Console Output (INFO and above)
```
HH:MM:SS | LEVEL    | Message
```
**Example:**
```
14:23:45 | INFO     | ◆ USER ACTION: User jogged motor
14:23:46 | ERROR    | ✗ ERROR in MovePanAbs: ValueError: Invalid angle
```

### File Output (All levels with full details)
```
YYYY-MM-DD HH:MM:SS | LEVEL    | MODULE_NAME | function_name:line_number | Message
```
**Example:**
```
2026-02-14 14:23:45 | INFO     | USER_ACTION   | jogMotor:18         | ◆ USER ACTION: User jogged motor
2026-02-14 14:23:45 | INFO     | MotorsRoutes  | jogMotor:21         | Jogging Pan motor LEFT at speed 50
2026-02-14 14:23:45 | DEBUG    | MotorControl  | Jog:62              | → ENTER: Jog(50, True, MotorEnum.Pan)
```

## Log Message Types

### User Actions
All Flask routes and user interactions are logged with the decorator:
```python
@log_user_action("User jogged motor")
def jogMotor(direction: str, speed: str):
    ...
```

**Output:**
```
◆ USER ACTION: User jogged motor
```

### Function Entry/Exit (Debug Level)
Function calls can be decorated to track entry and exit:
```python
@log_function_call
def MyFunction(param1, param2):
    ...
```

**Output:**
```
→ ENTER: MyFunction('value1', 'value2')
← EXIT:  MyFunction() returned dict
```

## Key Modules and Their Logging

### Main Application Flow
- **Main.py**: Logs application startup, configuration loading, and shutdown
- **FlaskServer.py** (USER_ACTION, FlaskServer): Logs all web requests and server status
- **MotorControl.py** (MotorControl): Logs all motor commands and firing sequences
- **Detector.py** (Detector): Logs camera recording and detection events
- **IOControl.py** (IOControl): Logs GPIO pin operations

### Flask Routes
- **MotorsRoutes** (routes/motors.py): All motor control user actions
- **ImageProcessingRoutes** (routes/imageProcessing.py): All image processing user actions
- **USER_ACTION**: High-level user interaction summary

## How to Review Logs

### 1. Monitor in Real-Time
While the application is running, watch the console output:
```
14:23:45 | INFO     | ◆ USER ACTION: User moved aim motors to home
14:23:46 | INFO     | Motors aimed, waiting for spool
14:23:47 | INFO     | Motors spooled, firing chamber servo
14:23:47 | INFO     | Find and Fire sequence complete
```

### 2. Review Complete Log File
Open the daily log file in your text editor:
```bash
# On Windows
notepad logs\cam_tracking_20260214.log

# On Linux/Pi
cat logs/cam_tracking_20260214.log
```

### 3. Filter Logs by Level
Print only errors and warnings:
```bash
# On Windows PowerShell
Get-Content logs\cam_tracking_20260214.log | Select-String "ERROR|WARNING"

# On Linux/Pi
grep -E "ERROR|WARNING" logs/cam_tracking_20260214.log
```

### 4. Filter Logs by Module
View only motor control logs:
```bash
# On Windows PowerShell
Get-Content logs\cam_tracking_20260214.log | Select-String "MotorControl"

# On Linux/Pi
grep "MotorControl" logs/cam_tracking_20260214.log
```

### 5. Filter Logs by User Actions
View all user interactions:
```bash
# On Windows PowerShell
Get-Content logs\cam_tracking_20260214.log | Select-String "USER_ACTION|◆"

# On Linux/Pi
grep "USER_ACTION\|◆" logs/cam_tracking_20260214.log
```

### 6. Find Detection Events
View all motion detection and firing sequences:
```bash
# On Windows PowerShell
Get-Content logs\cam_tracking_20260214.log | Select-String "Motion detected|Find and Fire|detection"

# On Linux/Pi
grep -i "motion detected\|find and fire\|detection" logs/cam_tracking_20260214.log
```

## Log Analysis Examples

### Example 1: Complete User Session
```
2026-02-14 14:23:45 | INFO     | Main | startServer:35 | STARTING FLASK SERVER ON 0.0.0.0:5000
2026-02-14 14:23:46 | INFO     | USER_ACTION | startStream:9 | ◆ USER ACTION: User started camera stream
2026-02-14 14:23:46 | DEBUG | FlaskServer | startStream:87 | Starting stream
2026-02-14 14:23:50 | INFO     | USER_ACTION | jogMotor:18 | ◆ USER ACTION: User jogged motor
2026-02-14 14:23:50 | INFO     | MotorsRoutes | jogMotor:21 | Jogging Pan motor LEFT at speed 50
2026-02-14 14:23:50 | DEBUG | MotorControl | Jog:62 | Jogging Pan motor at speed 50 direction forward
2026-02-14 14:23:55 | INFO     | USER_ACTION | stopStream:15 | ◆ USER ACTION: User stopped camera stream
```

### Example 2: Error Tracking
```
2026-02-14 14:25:30 | ERROR | MotorControl | MovePanAbs:42 | ✗ ERROR in MovePanAbs: ValueError: Invalid position 999
Traceback (most recent call last):
  File "motors/MotorControl.py", line 42, in MovePanAbs
    ...
ValueError: Invalid position 999
```

### Example 3: Detection and Firing
```
2026-02-14 14:26:15 | INFO     | Detector | _setDetectedLocation:55 | Detection found at location: X=15.5, Y=-8.2
2026-02-14 14:26:15 | DEBUG | Detector | _notifyObservers:68 | Observers notified of detection
2026-02-14 14:26:15 | INFO     | MotorControl | OnMotionFound:108 | Motion detected at location (15.5, -8.2). Act on detection = True
2026-02-14 14:26:15 | INFO     | MotorControl | FindAndFire:118 | Starting Find and Fire sequence
2026-02-14 14:26:15 | INFO     | MotorControl | FindAndFire:122 | Calculated motor adjustments - Pan: 7.75 degrees, Tilt: -4.1 degrees
2026-02-14 14:26:15 | DEBUG | MotorControl | FindAndFire:123 | Motors aimed, waiting for spool
2026-02-14 14:26:16 | INFO     | MotorControl | FindAndFire:126 | Motors spooled, firing chamber servo
2026-02-14 14:26:16 | INFO     | MotorControl | FindAndFire:130 | Find and Fire sequence complete
```

## Configuration

The logging system is configured in [LoggerSetup.py](LoggerSetup.py):

- **Log Directory**: `logs/` (created automatically)
- **File Max Size**: 10 MB (before rotation)
- **Backup Files**: 5 (maintains 50 MB of history)
- **File Log Level**: DEBUG (all messages)
- **Console Log Level**: INFO (important messages only)
- **Date Format**: `YYYY-MM-DD HH:MM:SS`

To modify settings, edit the `LoggerSetup.get_logger()` function parameters.

## Best Practices

1. **Review logs after each test session** to identify issues
2. **Filter by module** when debugging specific components
3. **Check for ERROR and EXCEPTION messages** regularly
4. **Monitor USER_ACTION logs** to understand user behavior
5. **Keep old logs** for historical analysis and troubleshooting
6. **Archive logs** periodically to prevent disk storage issues

## Troubleshooting

### No log files created
- Ensure the `logs/` directory has write permissions
- Check that LoggerSetup.py is imported before any logging calls

### Old logs not being cleaned up
- Backup files are kept when exceeding 50 MB total
- Manually delete old logs from the `logs/` directory as needed

### Missing logs for specific events
- Check the log level (DEBUG messages only appear in files, not console)
- Verify the module name matches what you're searching for
- Check if an exception occurred that prevented logging

## Support

For detailed logging information about specific modules, refer to the docstrings in LoggerSetup.py and the individual module files.
