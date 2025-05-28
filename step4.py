import json
from log_config import get_logger

# Configure logger for this step
logger = get_logger("step4")

def json_final_summary(input_data: dict, save_path: str = None) -> dict:
    """
    Multiply the summary by 10 and create final result.
    """
    logger.info("Starting step4 - Creating final summary")
    
    # Multiply summary by 10 for final result
    final_result_value = input_data["summary"] * 10
    
    result = {
        "raw_data": input_data["raw_data"],
        "processed_data": input_data["processed_data"],
        "summary": input_data["summary"],
        "final_result": final_result_value
    }
    
    # Save to file if path is provided
    if save_path:
        with open(save_path, 'w') as f:
            json.dump(result, f, indent=2)
        logger.info(f"Final summary written to {save_path}")
    
    logger.info("Step4 completed successfully")
    return result 