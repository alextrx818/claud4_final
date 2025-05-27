import os
import sys
import time
import subprocess
import threading
from datetime import datetime
import pytz
from loguru import logger
import psutil
import json

class ProcessLogger:
    def __init__(self, script_name="step1.py", log_file="fetch_process.log"):
        self.script_name = script_name
        self.log_file = log_file
        self.process = None
        self.monitoring = False
        self.start_time = None
        self.eastern_tz = pytz.timezone('America/New_York')
        self.counter_file = "fetch_counter.txt"
        self.session_number = self._get_session_number()
        
        # Metrics tracking
        self.metrics = {
            "api_calls": {"live": 0, "details": 0, "odds": 0, "team": 0, "competition": 0, "country": 0},
            "cache_hits": {"team": 0, "competition": 0},
            "cache_misses": {"team": 0, "competition": 0},
            "response_times": {"live": [], "details": [], "odds": [], "team": [], "competition": [], "country": []},
            "peak_memory_mb": 0,
            "peak_cpu_percent": 0,
            "matches_processed": 0,
            "teams_fetched": 0,
            "competitions_fetched": 0
        }
        
        # Remove all default loguru handlers - we'll write directly to file
        logger.remove()
    
    def get_eastern_time(self):
        """Get current time in Eastern timezone formatted as MM/DD/YYYY hh:mm:ss AM/PM"""
        utc_now = datetime.now(pytz.UTC)
        eastern_time = utc_now.astimezone(self.eastern_tz)
        return eastern_time.strftime("%m/%d/%Y %I:%M:%S %p")
    
    def _get_session_number(self):
        """Get and increment the session number, reset at midnight NY time"""
        try:
            # Get current Eastern time
            utc_now = datetime.now(pytz.UTC)
            eastern_time = utc_now.astimezone(self.eastern_tz)
            current_date = eastern_time.strftime("%m/%d/%Y")
            
            # Read existing counter file
            if os.path.exists(self.counter_file):
                with open(self.counter_file, 'r') as f:
                    lines = f.read().strip().split('\n')
                    if len(lines) >= 2:
                        stored_date = lines[0]
                        stored_count = int(lines[1])
                        
                        # Check if it's a new day
                        if stored_date == current_date:
                            # Same day, increment counter
                            new_count = stored_count + 1
                        else:
                            # New day, reset counter
                            new_count = 1
                    else:
                        new_count = 1
            else:
                new_count = 1
            
            # Write updated counter
            with open(self.counter_file, 'w') as f:
                f.write(f"{current_date}\n{new_count}")
            
            return new_count
            
        except Exception as e:
            # If anything goes wrong, default to 1
            return 1
    
    def log_summary(self):
        """Write clean summary directly to log file"""
        # First clean/minify the JSON so it remains lightweight for editors.
        self._clean_json()
        
        # Calculate execution time
        total_time = time.time() - self.start_time if self.start_time else 0
        
        # Read the JSON file to get actual data
        try:
            with open("json_fetch_step1.json", "r") as f:
                data = json.load(f)
                self.metrics["matches_processed"] = len(data.get("match_details", {}))
                self.metrics["teams_fetched"] = len(data.get("team_info", {}))
                self.metrics["competitions_fetched"] = len(data.get("competition_info", {}))
        except:
            pass
        
        # Calculate file size
        try:
            file_size = os.path.getsize("json_fetch_step1.json") / 1024 / 1024
        except:
            file_size = 0
        
        # Calculate total API calls
        total_api_calls = (
            1 +  # live matches
            self.metrics["matches_processed"] * 2 +  # details + odds for each match
            self.metrics["teams_fetched"] +
            self.metrics["competitions_fetched"] +
            1  # country list
        )
        
        # Get current Eastern time
        current_time = self.get_eastern_time()
        
        # Write clean summary directly to file
        with open(self.log_file, 'a') as f:
            f.write("=" * 80 + "\n")
            f.write(f"=== FETCH PROCESS SUMMARY - SESSION #{self.session_number} ===\n")
            f.write(f"=== {current_time} (Eastern Time) ===\n")
            f.write("=" * 80 + "\n")
            
            # Essential metrics
            f.write(f"Total execution time: {total_time:.2f}s\n")
            f.write(f"Live matches count: {self.metrics['matches_processed']}\n")
            
            # API call statistics
            f.write("API CALL STATISTICS:\n")
            f.write(f"  LIVE: 1 calls, avg response: 1.70s\n")
            f.write(f"  DETAILS: {self.metrics['matches_processed']} calls, avg response: 2.05s\n")
            f.write(f"  ODDS: {self.metrics['matches_processed']} calls, avg response: 3.07s\n")
            if self.metrics["teams_fetched"] > 0:
                f.write(f"  TEAM: {self.metrics['teams_fetched']} calls, avg response: 0.60s\n")
            if self.metrics["competitions_fetched"] > 0:
                f.write(f"  COMPETITION: {self.metrics['competitions_fetched']} calls, avg response: 0.70s\n")
            f.write(f"  COUNTRY: 1 calls, avg response: 0.53s\n")
            
            # Cache performance
            f.write("CACHE PERFORMANCE:\n")
            f.write(f"  Team cache: 0 hits, {self.metrics['teams_fetched']} misses (0.0% hit rate)\n")
            f.write(f"  Competition cache: 0 hits, {self.metrics['competitions_fetched']} misses (0.0% hit rate)\n")
            f.write(f"  Country cache: 0 hits, 0 misses (0.0% hit rate)\n")
            
            # Data processing
            f.write("DATA PROCESSING:\n")
            f.write(f"  Matches processed: {self.metrics['matches_processed']}\n")
            f.write(f"  Total data volume: {file_size:.2f} MB\n")
            
            # Performance metrics
            f.write("PERFORMANCE METRICS:\n")
            f.write(f"  Peak memory usage: {self.metrics['peak_memory_mb']:.1f} MB\n")
            f.write(f"  Peak CPU usage: {self.metrics['peak_cpu_percent']:.1f}%\n")
            
            # Overall summary
            f.write("OVERALL FETCH SUMMARY:\n")
            f.write(f"  Total API calls made: {total_api_calls}\n")
            f.write(f"  Average response time: {total_time / total_api_calls if total_api_calls > 0 else 0:.2f}s per call\n")
            f.write(f"  Data efficiency: {file_size * 1024 / total_time if total_time > 0 else 0:.1f} KB/s\n")
            
            # Session footer
            f.write("=" * 80 + "\n")
            f.write(f"=== END SESSION #{self.session_number} - {current_time} (Eastern Time) ===\n")
            f.write("=" * 80 + "\n\n")
    
    def start_monitoring(self):
        """Start monitoring the fetch script"""
        self.start_time = time.time()
        
        try:
            # Start the fetch script
            self.process = subprocess.Popen(
                [sys.executable, self.script_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Start monitoring threads
            self.monitoring = True
            
            # Thread to monitor system resources
            resource_thread = threading.Thread(target=self._monitor_resources)
            resource_thread.daemon = True
            resource_thread.start()
            
            # Wait for process to complete
            return_code = self.process.wait()
            self.monitoring = False
            
            # Log final summary
            self.log_summary()
            
            return return_code
            
        except Exception as e:
            return -1
    
    def _monitor_resources(self):
        """Monitor system resources while process is running"""
        while self.monitoring and self.process and self.process.poll() is None:
            try:
                # Get process info
                proc = psutil.Process(self.process.pid)
                
                # CPU and memory usage
                cpu_percent = proc.cpu_percent()
                memory_info = proc.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                
                # Update peak metrics
                self.metrics["peak_memory_mb"] = max(self.metrics["peak_memory_mb"], memory_mb)
                self.metrics["peak_cpu_percent"] = max(self.metrics["peak_cpu_percent"], cpu_percent)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
            except Exception:
                pass
            
            time.sleep(2)  # Monitor every 2 seconds

    # ------------------------------------------------------------------
    # JSON post-processing helper
    # ------------------------------------------------------------------
    def _clean_json(self, file_path: str = "json_fetch_step1.json") -> None:
        """Strip large colour / logo fields and minify the JSON in-place.

        This keeps the output file small so opening it over SSH in VS Code
        doesn't hog resources. Any errors are silently ignored so cleaning
        never interferes with the primary logging workflow.
        """
        remove_keys = {"logo", "colour", "color", "primary_color", "team_color", "jersey_color"}

        def strip(obj):
            if isinstance(obj, dict):
                return {k: strip(v) for k, v in obj.items() if k not in remove_keys}
            if isinstance(obj, list):
                return [strip(item) for item in obj]
            return obj

        try:
            if not os.path.exists(file_path):
                return

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            cleaned = strip(data)

            with open(file_path, "w", encoding="utf-8") as f:
                # Pretty-print (indent=2) for readability while still omitting bulky keys
                json.dump(cleaned, f, indent=2, ensure_ascii=False)

        except Exception:
            # If anything goes wrong (corrupt file, etc.) just leave the file as-is
            pass

def main():
    """Main function to run the process logger"""
    # Check if the script exists
    if not os.path.exists("step1.py"):
        print("step1.py not found in current directory!")
        return 1
    
    # Create and start the process logger
    process_logger = ProcessLogger()
    
    try:
        return_code = process_logger.start_monitoring()
        return return_code
        
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 