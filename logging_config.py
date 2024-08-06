import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_filename = "app.log"
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(log_filename, maxBytes=10*1024*1024, backupCount=5),  # Rotate log after 10MB
            logging.StreamHandler()
        ]
    )
