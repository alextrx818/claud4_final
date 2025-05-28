#!/usr/bin/env python3
"""Test script to run one pipeline cycle and show all output"""

import asyncio
import sys
import os

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

async def test_pipeline():
    """Run the complete pipeline once"""
    try:
        print("=== Starting test pipeline cycle ===")
        
        # Step 1: Fetch data
        print("Running Step 1: Data fetch")
        fetched_data = await step1_main()
        
        # Step 2: Extract, merge, summarize
        print("Running Step 2: Extract, merge, summarize")
        summaries = await extract_merge_summarize(fetched_data)
        
        # Step 3: JSON summary and grouping
        print("Running Step 3: JSON summary and grouping")
        summary_data = await json_summary(summaries)
        
        # Step 4: JSON final summary
        print("Running Step 4: JSON final summary")
        final_summary = await json_final_summary(summary_data)
        
        print(f"Pipeline completed successfully. Processed {len(summaries)} match summaries.")
        print(f"Step 4 generated {final_summary.get('total_matches', 0)} final summaries")
        
    except Exception as e:
        print(f"Pipeline failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pipeline()) 