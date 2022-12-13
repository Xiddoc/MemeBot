"""
Configuration of the logging.
"""
import logging
from config import LOG_TO_CONSOLE


log_path: str = './debug.log'

# Level config
levels = {
    logging.DEBUG: "[+]",
    logging.INFO: "[+]",
    logging.WARN: "[!]",
    logging.ERROR: "[-]",
}

# Set the level names
for level, level_text in levels.items():
    logging.addLevelName(level, level_text)

# Get the logger we will use everywhere
log = logging.getLogger()
log.setLevel(logging.INFO)

# Set the format
logFormatter = logging.Formatter('[%(asctime)s] %(levelname)s %(message)s')

# Create file handler and add it to the logger
fileHandler = logging.FileHandler(log_path)
fileHandler.setFormatter(logFormatter)
log.addHandler(fileHandler)

# Create console handler and add it to the logger
if LOG_TO_CONSOLE:
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    log.addHandler(consoleHandler)
