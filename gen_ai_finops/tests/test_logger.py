"""
Tests for structured logging
"""
import pytest
import os
import sys
from io import StringIO
from utils.logger import StructuredLogger


class TestStructuredLogger:
    """Test structured logging functionality."""
    
    def test_logger_initialization(self):
        """Test logger initialization."""
        logger = StructuredLogger("test_logger")
        
        assert logger.logger is not None
        assert logger.logger.name == "test_logger"
    
    def test_log_info(self, capsys):
        """Test info logging."""
        logger = StructuredLogger("test")
        logger.info("Test message", key="value")
        
        # Check that something was logged
        captured = capsys.readouterr()
        assert "Test message" in captured.out or "test" in captured.out.lower()
    
    def test_log_error(self, capsys):
        """Test error logging."""
        logger = StructuredLogger("test")
        logger.error("Error message", error_code=500)
        
        captured = capsys.readouterr()
        assert "error" in captured.out.lower() or "Error message" in captured.out
    
    def test_log_with_extra_fields(self, capsys):
        """Test logging with extra fields."""
        logger = StructuredLogger("test")
        logger.info("Message", user="testuser", action="test_action")
        
        captured = capsys.readouterr()
        # Should log something
        assert len(captured.out) > 0

