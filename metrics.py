"""
Metrics tracking system for pipeline performance monitoring.
"""

import time
import json
from typing import Dict, Any
from log_config import get_logger, get_run_id, get_timestamp

logger = get_logger("metrics")

class MetricsCollector:
    """Collects and tracks metrics for pipeline execution."""
    
    def __init__(self):
        self.metrics = {
            "run_id": get_run_id(),
            "start_time": get_timestamp(),
            "steps": {},
            "total_items_processed": 0,
            "total_duration": 0.0,
            "pipeline_status": "running"
        }
        self.step_start_times = {}
    
    def start_step(self, step_name: str):
        """Mark the start of a step."""
        self.step_start_times[step_name] = time.time()
        logger.info(f"Started timing for {step_name}")
    
    def end_step(self, step_name: str, items_processed: int = 0, additional_metrics: Dict[str, Any] = None):
        """Mark the end of a step and record metrics."""
        if step_name not in self.step_start_times:
            logger.warning(f"No start time recorded for {step_name}")
            return
        
        duration = time.time() - self.step_start_times[step_name]
        
        step_metrics = {
            "duration_seconds": round(duration, 4),
            "items_processed": items_processed,
            "items_per_second": round(items_processed / duration, 2) if duration > 0 else 0,
            "timestamp": get_timestamp(),
            "status": "completed"
        }
        
        if additional_metrics:
            step_metrics.update(additional_metrics)
        
        self.metrics["steps"][step_name] = step_metrics
        self.metrics["total_items_processed"] += items_processed
        
        logger.info(f"Step {step_name} completed in {duration:.4f}s, processed {items_processed} items")
        
        # Clean up
        del self.step_start_times[step_name]
    
    def record_error(self, step_name: str, error_message: str):
        """Record an error for a step."""
        if step_name in self.step_start_times:
            duration = time.time() - self.step_start_times[step_name]
            self.metrics["steps"][step_name] = {
                "duration_seconds": round(duration, 4),
                "status": "failed",
                "error": error_message,
                "timestamp": get_timestamp()
            }
            del self.step_start_times[step_name]
        
        self.metrics["pipeline_status"] = "failed"
        logger.error(f"Error in {step_name}: {error_message}")
    
    def finalize(self):
        """Finalize metrics collection."""
        self.metrics["end_time"] = get_timestamp()
        self.metrics["total_duration"] = sum(
            step.get("duration_seconds", 0) 
            for step in self.metrics["steps"].values()
        )
        
        if self.metrics["pipeline_status"] == "running":
            self.metrics["pipeline_status"] = "completed"
        
        # Calculate overall performance
        total_duration = self.metrics["total_duration"]
        total_items = self.metrics["total_items_processed"]
        
        self.metrics["overall_performance"] = {
            "total_items_processed": total_items,
            "total_duration_seconds": round(total_duration, 4),
            "average_items_per_second": round(total_items / total_duration, 2) if total_duration > 0 else 0,
            "steps_completed": len([s for s in self.metrics["steps"].values() if s.get("status") == "completed"]),
            "steps_failed": len([s for s in self.metrics["steps"].values() if s.get("status") == "failed"])
        }
        
        logger.info(f"Pipeline completed - Total duration: {total_duration:.4f}s, Items processed: {total_items}")
    
    def save_metrics(self, filepath: str = "pipeline_metrics.json"):
        """Save metrics to a JSON file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.metrics, f, indent=2)
            logger.info(f"Metrics saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Return current metrics."""
        return self.metrics.copy()
    
    def log_summary(self):
        """Log a summary of metrics."""
        if "overall_performance" in self.metrics:
            perf = self.metrics["overall_performance"]
            logger.info(f"METRICS SUMMARY - Duration: {perf['total_duration_seconds']}s, "
                       f"Items: {perf['total_items_processed']}, "
                       f"Rate: {perf['average_items_per_second']} items/s, "
                       f"Success: {perf['steps_completed']}/{perf['steps_completed'] + perf['steps_failed']} steps") 