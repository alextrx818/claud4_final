import json
from log_config import get_logger
from schemas import validate_processed_data, ValidationError
from metrics import MetricsCollector

# Configure logger for this step
logger = get_logger("step2")

def extract_merge_summarize(input_data: dict, save_path: str = None, metrics_collector: MetricsCollector = None) -> dict:
    """
    Process raw data by multiplying each number by 2.
    Enhanced with schema validation and metrics tracking.
    """
    logger.info("Starting step2 - Processing and merging data")
    
    if metrics_collector:
        metrics_collector.start_step("step2")
    
    try:
        # Process the raw data - multiply each number by 2
        processed_data = [x * 2 for x in input_data["raw_data"]]
        
        result = {
            "raw_data": input_data["raw_data"],
            "processed_data": processed_data
        }
        
        # Validate schema and add metadata
        validated_data = validate_processed_data(result)
        
        # Save to file if path is provided
        if save_path:
            with open(save_path, 'w') as f:
                json.dump(validated_data, f, indent=2)
            logger.info(f"Processed data written to {save_path}")
        
        # Record metrics
        if metrics_collector:
            additional_metrics = {
                "data_size_bytes": len(json.dumps(validated_data)),
                "validation_passed": True,
                "processing_factor": 2.0,
                "input_sum": sum(input_data["raw_data"]),
                "output_sum": sum(processed_data)
            }
            metrics_collector.end_step("step2", len(processed_data), additional_metrics)
        
        logger.info("Step2 completed successfully")
        return validated_data
        
    except ValidationError as e:
        error_msg = f"Schema validation failed: {e}"
        logger.error(error_msg)
        if metrics_collector:
            metrics_collector.record_error("step2", error_msg)
        raise
    except Exception as e:
        error_msg = f"Unexpected error in step2: {e}"
        logger.error(error_msg)
        if metrics_collector:
            metrics_collector.record_error("step2", error_msg)
        raise 