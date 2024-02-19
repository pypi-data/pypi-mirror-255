import logging
import os
import sys
from logging.handlers import RotatingFileHandler


# Configuration
LOG_DIR = os.path.join(os.path.expanduser('~'), '.rmb')

# Create directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
simple_formatter = logging.Formatter('%(message)s')

# Common configurations for both loggers
log_file_path = os.path.join(LOG_DIR, 'sdk.log')
file_handler = RotatingFileHandler(log_file_path, maxBytes=1024 * 1024, backupCount=3)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(simple_formatter)

# Logger which writes to file only
log = logging.getLogger('sdklog')

log.setLevel(logging.DEBUG)
log.addHandler(console_handler)
log.addHandler(file_handler)




