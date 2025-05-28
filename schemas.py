"""
Schema validation for pipeline data structures.
Using built-in Python typing for validation without external dependencies.
"""

from typing import Dict, List, Union, Any
import json
from log_config import get_logger, get_run_id, get_timestamp

logger = get_logger("schemas")

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

def validate_raw_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate Step 1 raw data structure."""
    logger.info("Validating raw data schema")
    
    if not isinstance(data, dict):
        raise ValidationError("Data must be a dictionary")
    
    if "raw_data" not in data:
        raise ValidationError("Missing 'raw_data' key")
    
    if not isinstance(data["raw_data"], list):
        raise ValidationError("'raw_data' must be a list")
    
    if not all(isinstance(x, (int, float)) for x in data["raw_data"]):
        raise ValidationError("All items in 'raw_data' must be numbers")
    
    # Add metadata
    validated_data = {
        **data,
        "run_id": get_run_id(),
        "timestamp": get_timestamp(),
        "schema_version": "1.0",
        "step": "step1"
    }
    
    logger.info(f"Raw data validation successful - {len(data['raw_data'])} items")
    return validated_data

def validate_processed_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate Step 2 processed data structure."""
    logger.info("Validating processed data schema")
    
    if not isinstance(data, dict):
        raise ValidationError("Data must be a dictionary")
    
    required_keys = ["raw_data", "processed_data"]
    for key in required_keys:
        if key not in data:
            raise ValidationError(f"Missing '{key}' key")
    
    if not isinstance(data["processed_data"], list):
        raise ValidationError("'processed_data' must be a list")
    
    if len(data["raw_data"]) != len(data["processed_data"]):
        raise ValidationError("raw_data and processed_data must have same length")
    
    # Add metadata
    validated_data = {
        **data,
        "run_id": get_run_id(),
        "timestamp": get_timestamp(),
        "schema_version": "1.0",
        "step": "step2"
    }
    
    logger.info(f"Processed data validation successful - {len(data['processed_data'])} items")
    return validated_data

def validate_summary_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate Step 3 summary data structure."""
    logger.info("Validating summary data schema")
    
    if not isinstance(data, dict):
        raise ValidationError("Data must be a dictionary")
    
    required_keys = ["raw_data", "processed_data", "summary"]
    for key in required_keys:
        if key not in data:
            raise ValidationError(f"Missing '{key}' key")
    
    if not isinstance(data["summary"], (int, float)):
        raise ValidationError("'summary' must be a number")
    
    # Add metadata
    validated_data = {
        **data,
        "run_id": get_run_id(),
        "timestamp": get_timestamp(),
        "schema_version": "1.0",
        "step": "step3"
    }
    
    logger.info(f"Summary data validation successful - summary value: {data['summary']}")
    return validated_data

def validate_final_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate Step 4 final data structure."""
    logger.info("Validating final data schema")
    
    if not isinstance(data, dict):
        raise ValidationError("Data must be a dictionary")
    
    required_keys = ["raw_data", "processed_data", "summary", "final_result"]
    for key in required_keys:
        if key not in data:
            raise ValidationError(f"Missing '{key}' key")
    
    if not isinstance(data["final_result"], (int, float)):
        raise ValidationError("'final_result' must be a number")
    
    # Add metadata
    validated_data = {
        **data,
        "run_id": get_run_id(),
        "timestamp": get_timestamp(),
        "schema_version": "1.0",
        "step": "step4"
    }
    
    logger.info(f"Final data validation successful - final result: {data['final_result']}")
    return validated_data 