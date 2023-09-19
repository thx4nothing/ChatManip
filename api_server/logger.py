import logging
import os
from logging.handlers import RotatingFileHandler

debug = int(os.getenv("CHATMANIP_DEBUG")) == 1

logger = logging.getLogger(__name__)

logs_directory = "logs"
if not os.path.exists(logs_directory):
    os.makedirs(logs_directory)

# Create a RotatingFileHandler for file logging
file_handler = RotatingFileHandler('logs/chatmanip.log', maxBytes=1024 * 1024, backupCount=5)
file_handler.setLevel(logging.DEBUG if debug else logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Create a StreamHandler for console logging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG if debug else logging.INFO)

# Add both handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
