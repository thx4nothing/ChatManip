import logging
import os
from logging.handlers import RotatingFileHandler

debug = int(os.getenv("CHATMANIP_DEBUG")) == 1
loglevel = logging.DEBUG if debug else logging.INFO

logs_directory = "data/logs"
if not os.path.exists(logs_directory):
    os.makedirs(logs_directory)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a RotatingFileHandler for file logging
file_handler = RotatingFileHandler(logs_directory + '/chatmanip.log', maxBytes=1024 * 1024,
                                   backupCount=5)
file_handler.setLevel(loglevel)
file_handler.setFormatter(formatter)

# Create a StreamHandler for console logging
console_handler = logging.StreamHandler()
console_handler.setLevel(loglevel)
console_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(loglevel)

# Add both handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
