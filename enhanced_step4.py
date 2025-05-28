import json
from log_config import get_logger
from schemas import validate_final_data, ValidationError
from metrics import MetricsCollector

# Configure logger for this step
logger = get_logger("step4")

def json_final_summary(input_data: dict, save_path: str = None, metrics_collector: MetricsCollector = None) -> dict:
    """
    Multiply the summary by 10 and create final result.
    Enhanced with schema validation and metrics tracking.
    """
    logger.info("Starting step4 - Creating final summary")
    
    if metrics_collector:
        metrics_collector.start_step("step4")
    
    try:
        # Multiply summary by 10 for final result
        final_result_value = input_data["summary"] * 10
        
        result = {
            "raw_data": input_data["raw_data"],
            "processed_data": input_data["processed_data"],
            "summary": input_data["summary"],
            "final_result": final_result_value
        }
        
        # Validate schema and add metadata
        validated_data = validate_final_data(result)
        
        # Save to file if path is provided
        if save_path:
            with open(save_path, 'w') as f:
                json.dump(validated_data, f, indent=2)
            logger.info(f"Final summary written to {save_path}")
        
        # Record metrics
        if metrics_collector:
            additional_metrics = {
                "data_size_bytes": len(json.dumps(validated_data)),
                "validation_passed": True,
                "final_result_value": final_result_value,
                "amplification_factor": 10.0,
                "total_transformation_ratio": round(final_result_value / sum(input_data["raw_data"]), 2)
            }
            metrics_collector.end_step("step4", 1, additional_metrics)  # 1 final result produced
        
        logger.info("Step4 completed successfully")
        return validated_data
        
    except ValidationError as e:
        error_msg = f"Schema validation failed: {e}"
        logger.error(error_msg)
        if metrics_collector:
            metrics_collector.record_error("step4", error_msg)
        raise
    except Exception as e:
        error_msg = f"Unexpected error in step4: {e}"
        logger.error(error_msg)
        if metrics_collector:
            metrics_collector.record_error("step4", error_msg)
        raise 