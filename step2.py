import json
from log_config import get_logger

# Configure logger for this step
logger = get_logger("step2")

def extract_merge_summarize(input_data: dict, save_path: str = None) -> dict:
    """
    Process raw data by multiplying each number by 2.
    """
    logger.info("Starting step2 - Processing and merging data")
    
    # Process the raw data - multiply each number by 2
    processed_data = [x * 2 for x in input_data["raw_data"]]
    
    result = {
        "raw_data": input_data["raw_data"],
        "processed_data": processed_data
    }
    
    # Save to file if path is provided
    if save_path:
        with open(save_path, 'w') as f:
            json.dump(result, f, indent=2)
        logger.info(f"Processed data written to {save_path}")
    
    logger.info("Step2 completed successfully")
    return result 