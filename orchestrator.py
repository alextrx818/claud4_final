#!/usr/bin/env python3
"""
FOOTBALL BOT ORCHESTRATOR
========================
Main orchestrator that runs the complete pipeline in a loop.
This is the only file that should contain scheduling logic.
"""

import asyncio
import sys
import os
from datetime import datetime
import logging
from zoneinfo import ZoneInfo

# ---------------------------------------------------------------------------
# Force logging timestamps to US Eastern Time in MM/DD/YYYY hh:mm:ss AM/PM
# ---------------------------------------------------------------------------

ET_TZ = ZoneInfo("America/New_York")

# Override the default time converter for logging.Formatter BEFORE basicConfig
logging.Formatter.converter = lambda *args: datetime.now(ET_TZ).timetuple()
DATE_FMT = "%m/%d/%Y %I:%M:%S %p"

# Add paths for importing step modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'Step1_json_fetch_logger'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'Step2_extract_merge_summarize'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'Step3_json_summary'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'Step4_json_final_summary'))

# Import step functions
from step1 import step1_main
from step2 import extract_merge_summarize
from step3 import json_summary
from step4 import json_final_summary

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt=DATE_FMT,
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def run_pipeline_once():
    """Run the complete pipeline once: Step 1 -> Step 2 -> Step 3 -> (Future Steps)"""
    try:
        logger.info("=== Starting pipeline cycle ===")
        
        # Step 1: Fetch data
        logger.info("Running Step 1: Data fetch")
        fetched_data = await step1_main()
        
        # Step 2: Extract, merge, summarize
        logger.info("Running Step 2: Extract, merge, summarize")
        summaries = await extract_merge_summarize(fetched_data)
        
        # Step 3: JSON summary and grouping
        logger.info("Running Step 3: JSON summary and grouping")
        summary_data = await json_summary(summaries)
        
        # Step 4: JSON final summary
        logger.info("Running Step 4: JSON final summary")
        logger.info(f"Step 4 input data type: {type(summary_data)}")
        logger.info(f"Step 4 input match_count: {summary_data.get('match_count', 'No match_count') if isinstance(summary_data, dict) else 'Not a dict'}")
        final_summary = await json_final_summary(summary_data)
        logger.info(f"Step 4 output total_matches: {final_summary.get('total_matches', 'No total_matches') if isinstance(final_summary, dict) else 'Not a dict'}")
        
        # Future steps would go here:
        # result3 = await step3(summaries)
        # await step4(result3)
        
        logger.info(f"Pipeline cycle completed successfully. Processed {len(summaries)} match summaries.")
        return True
        
    except Exception as e:
        logger.error(f"Pipeline cycle failed: {e}")
        return False


async def main():
    """Main orchestrator loop - runs pipeline every 60 seconds"""
    logger.info("Football Bot Orchestrator starting...")
    
    cycle_count = 0
    
    while True:
        try:
            cycle_count += 1
            logger.info(f"Starting cycle #{cycle_count}")
            
            # Run the complete pipeline
            success = await run_pipeline_once()
            
            if success:
                logger.info(f"Cycle #{cycle_count} completed successfully")
            else:
                logger.warning(f"Cycle #{cycle_count} completed with errors")
            
            # Wait 60 seconds before next cycle
            logger.info("Waiting 60 seconds before next cycle...")
            await asyncio.sleep(60)
            
        except KeyboardInterrupt:
            logger.info("Orchestrator stopped by user")
            break
        except Exception as e:
            logger.error(f"Unexpected error in orchestrator: {e}")
            logger.info("Waiting 60 seconds before retry...")
            await asyncio.sleep(60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Orchestrator shutdown complete") 