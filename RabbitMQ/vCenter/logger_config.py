import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name: str) -> logging.Logger:
    """Configures and returns a logger with both file and console handlers."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(name)
    
    # Prevent adding handlers multiple times if instantiated repeatedly
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # File Handler: 5MB max size, keeps 5 rotated backups
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, "infrastructure.log"), 
            maxBytes=5*1024*1024, 
            backupCount=5
        )
        file_handler.setFormatter(formatter)

        # Console Handler: For standard out (Docker/Terminal)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger