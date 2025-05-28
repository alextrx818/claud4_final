import json
from log_config import get_logger
from schemas import validate_summary_data, ValidationError
from metrics import MetricsCollector

# Configure logger for this step
logger = get_logger("step3")

def json_summary(input_data: dict, save_path: str = None, metrics_collector: MetricsCollector = None) -> dict:
    """
    Calculate the sum of processed_data values and create a summary.
    Enhanced with schema validation and metrics tracking.
    """
    logger.info("Starting step3 - Creating data summary")
    
    if metrics_collector:
        metrics_collector.start_step("step3")
    
    try:
        # Calculate sum of processed data
        summary_value = sum(input_data["processed_data"])
        
        result = {
            "raw_data": input_data["raw_data"],
            "processed_data": input_data["processed_data"],
            "summary": summary_value
        }
        
        # Validate schema and add metadata
        validated_data = validate_summary_data(result)
        
        # Save to file if path is provided
        if save_path:
            with open(save_path, 'w') as f:
                json.dump(validated_data, f, indent=2)
            logger.info(f"Summary data written to {save_path}")
        
        # Record metrics
        if metrics_collector:
            additional_metrics = {
                "data_size_bytes": len(json.dumps(validated_data)),
                "validation_passed": True,
                "summary_value": summary_value,
                "data_reduction_ratio": round(1 / len(input_data["processed_data"]), 4),
                "average_value": round(summary_value / len(input_data["processed_data"]), 2)
            }
            metrics_collector.end_step("step3", 1, additional_metrics)  # 1 summary value produced
        
        logger.info("Step3 completed successfully")
        return validated_data
        
    except ValidationError as e:
        error_msg = f"Schema validation failed: {e}"
        logger.error(error_msg)
        if metrics_collector:
            metrics_collector.record_error("step3", error_msg)
        raise
    except Exception as e:
        error_msg = f"Unexpected error in step3: {e}"
        logger.error(error_msg)
        if metrics_collector:
            metrics_collector.record_error("step3", error_msg)
        raise 