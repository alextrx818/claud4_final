import json
from log_config import get_logger

# Configure logger for this step
logger = get_logger("step1")

def step1_main(save_path: str = None) -> dict:
    """
    Simulate raw data fetching by creating a dictionary with raw_data.
    """
    logger.info("Starting step1 - Raw data fetching")
    
    # Simulate raw data fetching
    raw_data = {
        "raw_data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    }
    
    # Save to file if path is provided
    if save_path:
        with open(save_path, 'w') as f:
            json.dump(raw_data, f, indent=2)
        logger.info(f"Raw data written to {save_path}")
    
    logger.info("Step1 completed successfully")
    return raw_data 