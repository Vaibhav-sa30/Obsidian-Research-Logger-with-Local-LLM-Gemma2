import sys
import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, command):
        self.command = command
        self.process = None
        self.start_process()

    def start_process(self):
        if self.process:
            print("\n[Launcher] Change detected! Restarting logger...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        
        # Determine the python executable (use the venv if we are in it)
        python_exe = sys.executable
        
        # Start the main process
        # We don't use pythonw here because the launcher handles the windowless-ness if needed,
        # or the user runs the launcher in a terminal to see logs.
        self.process = subprocess.Popen([python_exe, "main.py"])
        print(f"[Launcher] Started main.py (PID: {self.process.pid})")

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            # De-bounce slightly to avoid multiple restarts for one save
            time.sleep(0.5)
            self.start_process()

if __name__ == "__main__":
    path = "."
    print("="*50)
    print("Obsidian Logger Hot-Reload Launcher 🚀")
    print("Watching for changes in .py files...")
    print("="*50)
    
    event_handler = ReloadHandler([sys.executable, "main.py"])
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
    observer.join()
