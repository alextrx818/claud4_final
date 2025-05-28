import json
from log_config import get_logger
from schemas import validate_raw_data, ValidationError
from metrics import MetricsCollector

# Configure logger for this step
logger = get_logger("step1")

def step1_main(save_path: str = None, metrics_collector: MetricsCollector = None) -> dict:
    """
    Simulate raw data fetching by creating a dictionary with raw_data.
    Enhanced with schema validation and metrics tracking.
    """
    logger.info("Starting step1 - Raw data fetching")
    
    if metrics_collector:
        metrics_collector.start_step("step1")
    
    try:
        # Simulate raw data fetching
        raw_data = {
            "raw_data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        }
        
        # Validate schema and add metadata
        validated_data = validate_raw_data(raw_data)
        
        # Save to file if path is provided
        if save_path:
            with open(save_path, 'w') as f:
                json.dump(validated_data, f, indent=2)
            logger.info(f"Raw data written to {save_path}")
        
        # Record metrics
        if metrics_collector:
            additional_metrics = {
                "data_size_bytes": len(json.dumps(validated_data)),
                "validation_passed": True
            }
            metrics_collector.end_step("step1", len(raw_data["raw_data"]), additional_metrics)
        
        logger.info("Step1 completed successfully")
        return validated_data
        
    except ValidationError as e:
        error_msg = f"Schema validation failed: {e}"
        logger.error(error_msg)
        if metrics_collector:
            metrics_collector.record_error("step1", error_msg)
        raise
    except Exception as e:
        error_msg = f"Unexpected error in step1: {e}"
        logger.error(error_msg)
        if metrics_collector:
            metrics_collector.record_error("step1", error_msg)
        raise 