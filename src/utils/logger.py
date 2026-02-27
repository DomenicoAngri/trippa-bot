"""
Logger Configuration
Centralized logging setup for the application
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "trippa_bot",
    level: str = "INFO",
    log_file: Optional[str] = None,
    console: bool = True
) -> logging.Logger:
    """
    Setup application logger with consistent formatting
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (None to disable file logging)
        console: Whether to log to console
    
    Returns:
        Configured logger instance
    
    Example:
        >>> logger = setup_logger("my_bot", "DEBUG", "logs/bot.log")
        >>> logger.info("Bot started")
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger by name
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
