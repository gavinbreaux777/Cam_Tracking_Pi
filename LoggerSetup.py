"""
Centralized logging configuration for the Cam Tracking Pi project.
Provides file and console logging with consistent formatting.
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from functools import wraps
from typing import Any, Callable


class LoggerSetup:
    """Configures and manages application-wide logging."""
    
    _logger = None
    _log_dir = Path("logs")
    
    @classmethod
    def get_logger(cls, name: str = "CamTrackingPi") -> logging.Logger:
        """
        Get or create the application logger.
        
        Args:
            name: Logger name (default: "CamTrackingPi")
            
        Returns:
            Configured logger instance
        """
        # Only set up handlers once
        if cls._logger is None:
            # Create logs directory if it doesn't exist
            cls._log_dir.mkdir(exist_ok=True)
            
            # Create root logger for shared handlers
            cls._logger = logging.getLogger("CamTrackingPi")
            cls._logger.setLevel(logging.DEBUG)
            
            # Prevent duplicate handlers
            if cls._logger.hasHandlers():
                cls._logger.handlers.clear()
            
            # Create formatters
            detailed_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            console_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(message)s',
                datefmt='%H:%M:%S'
            )
            
            # File handler - all logs with detailed format
            log_file = cls._log_dir / f"cam_tracking_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            cls._logger.addHandler(file_handler)
            
            # Console handler - INFO and above with simpler format
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(console_formatter)
            cls._logger.addHandler(console_handler)
            
            cls._logger.info(f"Logger initialized. Logs will be written to {log_file}")
        
        # Return logger for the specific module using hierarchical naming
        # This creates a parent-child relationship so logs propagate to root logger's handlers
        logger_name = f"CamTrackingPi.{name}" if name != "CamTrackingPi" else name
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = True  # Ensure logs propagate to parent
        return logger


def log_function_call(func: Callable) -> Callable:
    """
    Decorator to log function entry, exit, and exceptions.
    
    Args:
        func: Function to be decorated
        
    Returns:
        Decorated function with logging
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        logger = LoggerSetup.get_logger(func.__module__)
        
        # Create parameter string for logging
        args_repr = [repr(a) for a in args[:3]]  # Limit to first 3 args to avoid clutter
        kwargs_repr = [f"{k}={v!r}" for k, v in list(kwargs.items())[:3]]
        
        if len(args) > 3:
            args_repr.append(f"... (+{len(args) - 3} more)")
        if len(kwargs) > 3:
            kwargs_repr.append(f"... (+{len(kwargs) - 3} more)")
        
        signature = ", ".join(args_repr + kwargs_repr)
        
        logger.debug(f"→ ENTER: {func.__name__}({signature})")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"← EXIT:  {func.__name__}() returned {type(result).__name__}")
            return result
        except Exception as e:
            logger.error(f"✗ ERROR in {func.__name__}: {type(e).__name__}: {str(e)}", 
                        exc_info=True)
            raise
    
    return wrapper


def log_user_action(action: str, level: str = "INFO") -> Callable:
    """
    Decorator to log user interactions/Flask routes.
    
    Args:
        action: Description of the user action
        level: Log level (default: "INFO")
        
    Returns:
        Decorated function with user action logging
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = LoggerSetup.get_logger("USER_ACTION")
            log_method = getattr(logger, level.lower(), logger.info)
            
            log_method(f"[USER ACTION] {action}")
            
            try:
                result = func(*args, **kwargs)
                logger.info(f"[USER ACTION COMPLETED] {action}")
                return result
            except Exception as e:
                logger.error(f"[USER ACTION FAILED] {action} - {type(e).__name__}: {str(e)}", 
                            exc_info=True)
                raise
        
        return wrapper
    return decorator


# Convenience function for quick logging
def get_logger(module_name: str = None) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        module_name: Optional module name for the logger
        
    Returns:
        Logger instance
    """
    if module_name:
        return logging.getLogger(module_name)
    return LoggerSetup.get_logger()
