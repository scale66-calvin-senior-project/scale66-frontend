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


class SmartFormatter(logging.Formatter):
    """
    Smart formatter that only shows logger name when it changes.
    
    This reduces repetitive "Orchestrator |" on every line while still
    showing context when different components log messages.
    """
    
    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt, datefmt)
        self.last_logger = None
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record, showing logger name only when it changes."""
        current_logger = record.name
        
        # Special handling for orchestrator - don't repeat name
        if current_logger == "Orchestrator":
            # Only show logger name for specific messages
            if any(keyword in record.getMessage() for keyword in [
                "PIPELINE START", "STEP ", "PIPELINE COMPLETE"
            ]):
                # These are section headers - no prefix needed
                return record.getMessage()
            else:
                # Regular orchestrator messages - no prefix
                return record.getMessage()
        
        # For other agents, show name only when it changes or for completion messages
        if current_logger != self.last_logger or "Completed" in record.getMessage():
            self.last_logger = current_logger
            # Show logger name for agent completion or when switching agents
            return f"{current_logger} | {record.getMessage()}"
        else:
            # Same logger continuing - no prefix
            return record.getMessage()
        
        return record.getMessage()


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
    # Use smart formatter that reduces repetitive logger names
    # This is for user-facing output logs, not debugging logs
    formatter = SmartFormatter()
    
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
    
    # Suppress all third-party library logs (only show errors)
    logging.getLogger("httpx").setLevel(logging.ERROR)
    logging.getLogger("httpcore").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("anthropic").setLevel(logging.ERROR)
    logging.getLogger("google").setLevel(logging.ERROR)
    logging.getLogger("google_genai").setLevel(logging.ERROR)
    logging.getLogger("google.genai").setLevel(logging.ERROR)
    logging.getLogger("google_genai.models").setLevel(logging.ERROR)
    
    # Logging initialized (no log message - this is internal setup)


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


def create_run_log_file(run_id: str) -> logging.Handler:
    """
    Create a new file handler for a specific pipeline run.
    
    This creates a timestamped log file for a single execution:
    logs/scale66_2024-11-28_18-34-39_abc123.log
    
    Args:
        run_id: Unique identifier for this run (e.g., carousel_id or brand_kit_id)
    
    Returns:
        FileHandler instance configured for this run
    
    Usage:
        # At start of pipeline run
        handler = create_run_log_file(carousel_id)
        
        # At end of pipeline run
        logging.getLogger().removeHandler(handler)
        handler.close()
    """
    from datetime import datetime
    
    # Create timestamp for filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Create filename: scale66_YYYY-MM-DD_HH-MM-SS_runid.log
    short_run_id = run_id[:8] if len(run_id) > 8 else run_id
    log_filename = f"scale66_{timestamp}_{short_run_id}.log"
    
    # Determine log file path
    if settings.log_file:
        log_dir = Path(settings.log_file).parent
    else:
        log_dir = Path("logs")
    
    log_path = log_dir / log_filename
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create file handler with smart formatter
    formatter = SmartFormatter()
    
    file_handler = logging.FileHandler(
        filename=log_path,
        mode='w',  # Write mode - new file each time
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Add to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    
    # Note: Don't log the file creation to the file itself
    # (that's internal info, not user-facing pipeline info)
    
    return file_handler

