import logging
import logging.handlers
from datetime import datetime
import sys

def setup_logger():
    # Create logger
    logger = logging.getLogger('DynatraceAPI')
    logger.setLevel(logging.DEBUG)

    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s'
    )

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)

    return logger 