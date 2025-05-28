import json
from log_config import get_logger

# Configure logger for this step
logger = get_logger("step3")

def json_summary(input_data: dict, save_path: str = None) -> dict:
    """
    Calculate the sum of processed_data values and create a summary.
    """
    logger.info("Starting step3 - Creating data summary")
    
    # Calculate sum of processed data
    summary_value = sum(input_data["processed_data"])
    
    result = {
        "raw_data": input_data["raw_data"],
        "processed_data": input_data["processed_data"],
        "summary": summary_value
    }
    
    # Save to file if path is provided
    if save_path:
        with open(save_path, 'w') as f:
            json.dump(result, f, indent=2)
        logger.info(f"Summary data written to {save_path}")
    
    logger.info("Step3 completed successfully")
    return result 