import logging
import os
import uuid
from datetime import datetime
import pytz

# Global run ID for this execution
CURRENT_RUN_ID = str(uuid.uuid4())[:8]

def get_logger(name):
    """
    Returns a logger that writes to pipeline.log with the specified format.
    If the logger already has handlers, does not add another one.
    """
    logger = logging.getLogger(name)
    
    # If logger already has handlers, return it as-is
    if logger.handlers:
        return logger
    
    # Set logging level
    logger.setLevel(logging.INFO)
    
    # Create file handler for pipeline.log
    log_file = "pipeline.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Enhanced formatter: timestamp - run_id - logger name - log level - message
    formatter = logging.Formatter(f'%(asctime)s - {CURRENT_RUN_ID} - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(file_handler)
    
    return logger

def get_run_id():
    """Return the current run ID for this execution."""
    return CURRENT_RUN_ID

def get_timestamp():
    """Return current timestamp in New York Eastern time with MM/DD/YYYY format and AM/PM."""
    eastern = pytz.timezone('America/New_York')
    now = datetime.now(eastern)
    return now.strftime("%m/%d/%Y %I:%M:%S %p %Z") 