import json
import sys
import os
from step1 import step1_main
from step2 import extract_merge_summarize
from step3 import json_summary
from step4 import json_final_summary
from log_config import get_logger

# Configure logger for orchestrator
logger = get_logger("orchestrator")

def run_pipeline():
    """
    Run the complete 4-step pipeline with centralized logging.
    """
    logger.info("Starting pipeline execution")
    
    # Step 1: Raw data fetching
    logger.info("Executing Step 1 - Raw data fetching")
    data1 = step1_main(save_path="step1.json")
    
    # Step 2: Processing and merging
    logger.info("Executing Step 2 - Processing and merging")
    data2 = extract_merge_summarize(data1, save_path="step2.json")
    
    # Step 3: Summarization
    logger.info("Executing Step 3 - Summarization")
    data3 = json_summary(data2, save_path="step3.json")
    
    # Step 4: Final output
    logger.info("Executing Step 4 - Final output")
    final_output = json_final_summary(data3, save_path="step4.json")
    
    # Write final output to final_output.json
    with open("final_output.json", 'w') as f:
        json.dump(final_output, f, indent=2)
    
    logger.info("Pipeline execution completed successfully")
    logger.info(f"Final result: {final_output['final_result']}")
    
    return final_output

if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1) 