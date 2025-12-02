"""
Logging Configuration Module
Provides centralized logging setup for the entire application
"""
import logging
import sys
from datetime import datetime
from pathlib import Path

def setup_logger(name: str = "ECImageGenerator", log_level: int = logging.INFO, log_file: str = None) -> logging.Logger:
    """
    Setup and configure logger with both file and console handlers
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path. If None, creates logs/ directory
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create logs directory if needed
    if log_file is None:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"ec_image_generator_{timestamp}.log"
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        '%(levelname)-8s | %(name)s | %(message)s'
    )
    
    # File handler (detailed)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Console handler (simpler)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    logger.info(f"Logger initialized. Log file: {log_file}")
    logger.debug(f"Log level set to: {logging.getLevelName(log_level)}")
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """
    Get existing logger or create new one
    
    Args:
        name: Logger name (uses parent module name if None)
        
    Returns:
        Logger instance
    """
    if name is None:
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'ECImageGenerator')
    
    logger = logging.getLogger(name)
    if not logger.handlers:
        # If no handlers, setup default logger
        return setup_logger(name)
    return logger

