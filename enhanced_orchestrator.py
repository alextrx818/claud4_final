import json
import sys
import os
from enhanced_step1 import step1_main
from enhanced_step2 import extract_merge_summarize
from enhanced_step3 import json_summary
from enhanced_step4 import json_final_summary
from log_config import get_logger, get_run_id
from metrics import MetricsCollector
from schemas import ValidationError

# Configure logger for orchestrator
logger = get_logger("orchestrator")

def run_enhanced_pipeline():
    """
    Run the complete 4-step pipeline with enhanced features:
    - Run IDs and timestamps
    - Schema validation
    - Metrics tracking
    - Comprehensive error handling
    """
    run_id = get_run_id()
    logger.info(f"Starting enhanced pipeline execution - Run ID: {run_id}")
    
    # Initialize metrics collector
    metrics = MetricsCollector()
    
    try:
        # Step 1: Raw data fetching
        logger.info("Executing Step 1 - Raw data fetching with validation")
        data1 = step1_main(save_path="enhanced_step1.json", metrics_collector=metrics)
        
        # Step 2: Processing and merging
        logger.info("Executing Step 2 - Processing and merging with validation")
        data2 = extract_merge_summarize(data1, save_path="enhanced_step2.json", metrics_collector=metrics)
        
        # Step 3: Summarization
        logger.info("Executing Step 3 - Summarization with validation")
        data3 = json_summary(data2, save_path="enhanced_step3.json", metrics_collector=metrics)
        
        # Step 4: Final output
        logger.info("Executing Step 4 - Final output with validation")
        final_output = json_final_summary(data3, save_path="enhanced_step4.json", metrics_collector=metrics)
        
        # Write final output to enhanced_final_output.json
        with open("enhanced_final_output.json", 'w') as f:
            json.dump(final_output, f, indent=2)
        
        # Finalize metrics
        metrics.finalize()
        metrics.save_metrics("enhanced_pipeline_metrics.json")
        metrics.log_summary()
        
        logger.info("Enhanced pipeline execution completed successfully")
        logger.info(f"Final result: {final_output['final_result']} (Run ID: {run_id})")
        
        return final_output
        
    except ValidationError as e:
        error_msg = f"Pipeline failed due to validation error: {e}"
        logger.error(error_msg)
        metrics.finalize()
        metrics.save_metrics("enhanced_pipeline_metrics_failed.json")
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"Pipeline failed with unexpected error: {e}"
        logger.error(error_msg, exc_info=True)
        metrics.finalize()
        metrics.save_metrics("enhanced_pipeline_metrics_failed.json")
        sys.exit(1)

def demonstrate_features():
    """Demonstrate the enhanced features with detailed logging."""
    logger.info("=== ENHANCED PIPELINE DEMONSTRATION ===")
    logger.info("Features: Run IDs, Schema Validation, Metrics Tracking")
    
    result = run_enhanced_pipeline()
    
    logger.info("=== DEMONSTRATION COMPLETE ===")
    return result

if __name__ == "__main__":
    demonstrate_features() 