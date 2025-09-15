#!/usr/bin/env python3
"""
Script to start Celery worker and beat scheduler
Usage: python scripts/start_celery.py [worker|beat|both]
"""

import sys
import subprocess
import os
from pathlib import Path

def start_worker():
    """Start Celery worker"""
    print("Starting Celery worker...")
    cmd = ["celery", "-A", "celery_app", "worker", "--loglevel=info", "--concurrency=2"]
    return subprocess.Popen(cmd)

def start_beat():
    """Start Celery beat scheduler"""
    print("Starting Celery beat scheduler...")
    cmd = ["celery", "-A", "celery_app", "beat", "--loglevel=info"]
    return subprocess.Popen(cmd)

def main():
    # Change to backend directory
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)
    
    mode = sys.argv[1] if len(sys.argv) > 1 else "both"
    
    processes = []
    
    try:
        if mode in ["worker", "both"]:
            worker_process = start_worker()
            processes.append(worker_process)
        
        if mode in ["beat", "both"]:
            beat_process = start_beat()
            processes.append(beat_process)
        
        print(f"Celery services started in '{mode}' mode")
        print("Press Ctrl+C to stop all services")
        
        # Wait for processes
        for process in processes:
            process.wait()
            
    except KeyboardInterrupt:
        print("\nStopping Celery services...")
        for process in processes:
            process.terminate()
        print("All services stopped")

if __name__ == "__main__":
    main()