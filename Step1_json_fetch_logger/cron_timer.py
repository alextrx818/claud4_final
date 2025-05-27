#!/usr/bin/env python3
"""
Cron Timer for Football Bot JSON Fetch Step 1
This script is designed to be run by cron to automatically fetch football data
"""

import os
import sys
import time
import subprocess
import schedule
from datetime import datetime
import pytz
import logging

class CronTimer:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.json_fetch_script = os.path.join(self.script_dir, "json_fetch_step1.py")
        self.process_logger_script = os.path.join(self.script_dir, "process_logger.py")
        self.cron_log_file = os.path.join(self.script_dir, "cron_timer.log")
        self.lock_file = os.path.join(self.script_dir, "fetch_job.lock")
        self.eastern_tz = pytz.timezone('America/New_York')
        
        # Setup logging for cron activities
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.cron_log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_eastern_time(self):
        """Get current time in Eastern timezone"""
        utc_now = datetime.now(pytz.UTC)
        eastern_time = utc_now.astimezone(self.eastern_tz)
        return eastern_time.strftime("%m/%d/%Y %I:%M:%S %p")
    
    def acquire_lock(self):
        """Acquire lock to prevent concurrent executions"""
        try:
            if os.path.exists(self.lock_file):
                # Check if lock file is stale (older than 10 minutes)
                lock_age = time.time() - os.path.getmtime(self.lock_file)
                if lock_age > 600:  # 10 minutes
                    self.logger.warning("Removing stale lock file")
                    os.remove(self.lock_file)
                else:
                    return False
            
            # Create lock file with current timestamp
            with open(self.lock_file, 'w') as f:
                f.write(f"{time.time()}\n{os.getpid()}\n")
            return True
        except Exception as e:
            self.logger.error(f"Error acquiring lock: {str(e)}")
            return False
    
    def release_lock(self):
        """Release the lock file"""
        try:
            if os.path.exists(self.lock_file):
                os.remove(self.lock_file)
        except Exception as e:
            self.logger.error(f"Error releasing lock: {str(e)}")
    
    def run_fetch_job(self):
        """Run the JSON fetch job using process_logger.py"""
        # Try to acquire lock
        if not self.acquire_lock():
            self.logger.warning(f"Fetch job already running, skipping execution at {self.get_eastern_time()} (Eastern Time)")
            return
        
        try:
            self.logger.info(f"Starting scheduled fetch job at {self.get_eastern_time()} (Eastern Time)")
            
            # Change to script directory
            os.chdir(self.script_dir)
            
            # Run the process logger which will handle the JSON fetch
            result = subprocess.run(
                [sys.executable, "process_logger.py"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                self.logger.info(f"Fetch job completed successfully at {self.get_eastern_time()} (Eastern Time)")
            else:
                self.logger.error(f"Fetch job failed with return code {result.returncode}")
                if result.stderr:
                    self.logger.error(f"Error output: {result.stderr}")
                    
        except subprocess.TimeoutExpired:
            self.logger.error("Fetch job timed out after 5 minutes")
        except Exception as e:
            self.logger.error(f"Error running fetch job: {str(e)}")
        finally:
            # Always release the lock
            self.release_lock()
    
    def run_direct_fetch(self):
        """Run the JSON fetch script directly (without process_logger)"""
        # Try to acquire lock
        if not self.acquire_lock():
            self.logger.warning(f"Fetch job already running, skipping direct execution at {self.get_eastern_time()} (Eastern Time)")
            return
        
        try:
            self.logger.info(f"Starting direct fetch job at {self.get_eastern_time()} (Eastern Time)")
            
            # Change to script directory
            os.chdir(self.script_dir)
            
            # Run the JSON fetch script directly
            result = subprocess.run(
                [sys.executable, "json_fetch_step1.py"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                self.logger.info(f"Direct fetch job completed successfully at {self.get_eastern_time()} (Eastern Time)")
            else:
                self.logger.error(f"Direct fetch job failed with return code {result.returncode}")
                if result.stderr:
                    self.logger.error(f"Error output: {result.stderr}")
                    
        except subprocess.TimeoutExpired:
            self.logger.error("Direct fetch job timed out after 5 minutes")
        except Exception as e:
            self.logger.error(f"Error running direct fetch job: {str(e)}")
        finally:
            # Always release the lock
            self.release_lock()
    
    def setup_schedule(self):
        """Setup the schedule for automatic runs"""
        # Schedule options - uncomment the one you want to use:
        
        # Every 60 seconds (1 minute)
        schedule.every(60).seconds.do(self.run_fetch_job)
        
        # Every 15 minutes
        # schedule.every(15).minutes.do(self.run_fetch_job)
        
        # Every 30 minutes
        # schedule.every(30).minutes.do(self.run_fetch_job)
        
        # Every hour
        # schedule.every().hour.do(self.run_fetch_job)
        
        # Every 2 hours
        # schedule.every(2).hours.do(self.run_fetch_job)
        
        # Every 6 hours
        # schedule.every(6).hours.do(self.run_fetch_job)
        
        # Daily at specific times
        # schedule.every().day.at("09:00").do(self.run_fetch_job)
        # schedule.every().day.at("15:00").do(self.run_fetch_job)
        # schedule.every().day.at("21:00").do(self.run_fetch_job)
        
        self.logger.info("Schedule setup complete - running every 60 seconds (1 minute)")
    
    def run_scheduler(self):
        """Run the scheduler continuously"""
        self.logger.info(f"Cron Timer started at {self.get_eastern_time()} (Eastern Time)")
        self.setup_schedule()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info(f"Cron Timer stopped at {self.get_eastern_time()} (Eastern Time)")
        except Exception as e:
            self.logger.error(f"Scheduler error: {str(e)}")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        cron_timer = CronTimer()
        
        if command == "run":
            # Run once immediately
            cron_timer.run_fetch_job()
        elif command == "direct":
            # Run direct fetch once
            cron_timer.run_direct_fetch()
        elif command == "schedule":
            # Run the scheduler
            cron_timer.run_scheduler()
        elif command == "test":
            # Test run
            print(f"Current Eastern Time: {cron_timer.get_eastern_time()}")
            print(f"Script directory: {cron_timer.script_dir}")
            print(f"JSON fetch script: {cron_timer.json_fetch_script}")
            print(f"Process logger script: {cron_timer.process_logger_script}")
            print("Test completed successfully!")
        else:
            print("Usage:")
            print("  python3 cron_timer.py run      - Run fetch job once")
            print("  python3 cron_timer.py direct   - Run direct fetch once")
            print("  python3 cron_timer.py schedule - Start scheduler")
            print("  python3 cron_timer.py test     - Test configuration")
    else:
        print("Football Bot Cron Timer")
        print("Usage:")
        print("  python3 cron_timer.py run      - Run fetch job once")
        print("  python3 cron_timer.py direct   - Run direct fetch once")
        print("  python3 cron_timer.py schedule - Start scheduler")
        print("  python3 cron_timer.py test     - Test configuration")
        print("")
        print("For cron usage, add to crontab:")
        print("  # Every minute")
        print("  * * * * * cd /path/to/Football_bot/Step1_json_fetch_logger && python3 cron_timer.py run")
        print("")
        print("  # Every 30 minutes")
        print("  */30 * * * * cd /path/to/Football_bot/Step1_json_fetch_logger && python3 cron_timer.py run")
        print("")
        print("  # Every hour")
        print("  0 * * * * cd /path/to/Football_bot/Step1_json_fetch_logger && python3 cron_timer.py run")
        print("")
        print("  # Every 6 hours")
        print("  0 */6 * * * cd /path/to/Football_bot/Step1_json_fetch_logger && python3 cron_timer.py run")

if __name__ == "__main__":
    main() 