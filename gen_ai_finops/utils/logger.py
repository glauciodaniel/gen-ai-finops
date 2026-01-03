"""
Structured Logging Configuration
"""
import os
import sys
import json
import logging
from datetime import datetime
from typing import Any, Dict

try:
    from pythonjsonlogger import jsonlogger
    JSON_LOGGER_AVAILABLE = True
except ImportError:
    JSON_LOGGER_AVAILABLE = False


class StructuredLogger:
    """Structured JSON logger for GenAIFinOps."""
    
    def __init__(self, name: str = "gen_ai_finops"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, os.getenv("LOG_LEVEL", "INFO")))
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        
        # Use JSON formatter if LOG_FORMAT is json and available
        log_format = os.getenv("LOG_FORMAT", "json").lower()
        if log_format == "json" and JSON_LOGGER_AVAILABLE:
            formatter = jsonlogger.JsonFormatter(
                "%(timestamp)s %(level)s %(name)s %(message)s",
                timestamp=True
            )
        else:
            if log_format == "json" and not JSON_LOGGER_AVAILABLE:
                # Fallback to standard formatter if JSON logger not available
                formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s [JSON logger not installed]"
                )
            else:
                formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
        
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def _log(self, level: str, message: str, **kwargs):
        """Internal logging method with structured data."""
        log_format = os.getenv("LOG_FORMAT", "json").lower()
        
        if log_format == "json" and JSON_LOGGER_AVAILABLE:
            # JSON logger handles extra fields automatically
            extra = {
                "timestamp": datetime.utcnow().isoformat(),
                **kwargs
            }
            getattr(self.logger, level.lower())(message, extra=extra)
        else:
            # Standard logger - format message with extra info
            extra_info = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
            full_message = f"{message}" + (f" | {extra_info}" if extra_info else "")
            getattr(self.logger, level.lower())(full_message)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log("info", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log("error", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log("warning", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log("debug", message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log("critical", message, **kwargs)


# Global logger instance
logger = StructuredLogger()

