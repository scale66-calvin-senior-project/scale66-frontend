"""
Centralized Logging Configuration - Standardized logging setup for Scale66 backend.

Provides:
- Environment-aware logging configuration (development/production)
- Structured logging with consistent formatting
- Multiple handlers (console, file, optional JSON)
- Log rotation and size management
- Contextual logging support

Usage:
    from app.core.logging import setup_logging
    
    # In main.py application startup
    setup_logging()
    
    # In any module
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Message here")
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from app.core.config import settings


class ContextFilter(logging.Filter):
    """Add contextual information to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add extra context fields to log record."""
        # Add empty context fields if not present
        if not hasattr(record, 'request_id'):
            record.request_id = '-'
        if not hasattr(record, 'user_id'):
            record.user_id = '-'
        return True


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None
) -> None:
    """
    Configure centralized logging for the application.
    
    Args:
        log_level: Override log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Override log file path
    
    Features:
        - Console handler with colored output for development
        - File handler with rotation for production
        - Structured logging format with timestamps and context
        - Different configurations for dev/prod environments
    """
    # Determine log level
    if log_level is None:
        log_level = settings.log_level
    
    # Determine log file path
    if log_file is None:
        log_file = settings.log_file
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    if settings.environment == "production":
        # Production: Structured format with all details
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        # Development: Simpler format for readability
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
    
    # Console handler (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    console_handler.addFilter(ContextFilter())
    root_logger.addHandler(console_handler)
    
    # File handler (if enabled)
    if settings.log_to_file and log_file:
        # Use rotating file handler to prevent unlimited growth
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=settings.log_file_max_bytes,
            backupCount=settings.log_file_backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        file_handler.addFilter(ContextFilter())
        root_logger.addHandler(file_handler)
    
    # Set log levels for noisy third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    
    # Log initialization
    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging initialized: level={log_level.upper()}, "
        f"environment={settings.environment}, "
        f"file_logging={'enabled' if settings.log_to_file else 'disabled'}"
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured logger instance
    
    Note:
        This is a convenience function. You can also use logging.getLogger(__name__) directly.
    """
    return logging.getLogger(name)

