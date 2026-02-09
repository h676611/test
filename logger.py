import logging
import logging.handlers
from pathlib import Path
from datetime import datetime

# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

def setup_logger(name, log_file=None, level=logging.DEBUG):
    """
    Setup a logger for ZMQ clients and server.
    
    Args:
        name: Logger name (e.g., 'zmq_server', 'zmq_client')
        log_file: Optional log file path. If None, uses 'logs/{name}.log'
        level: Logging level (default: DEBUG)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.hasHandlers():
        return logger
    
    # File handler
    if log_file is None:
        log_file = log_dir / f"{name}.log"
    else:
        log_file = Path(log_file)
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5_000_000,  # 5MB
        backupCount=5
    )
    file_handler.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger