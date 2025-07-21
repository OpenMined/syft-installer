import os
import signal
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional

from syft_installer.config import Config
from syft_installer.exceptions import BinaryNotFoundError


class Launcher:
    """Handle SyftBox client process management."""
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.thread: Optional[threading.Thread] = None
    
    def start(self, config: Config, background: bool = False) -> None:
        """
        Start SyftBox client.
        
        Args:
            config: SyftBox configuration
            background: Run in background thread
        """
        if self.is_running():
            return
        
        # Check binary exists
        if not config.binary_path.exists():
            raise BinaryNotFoundError(f"SyftBox binary not found at {config.binary_path}")
        
        # Build command - just run syftbox (no subcommand needed)
        # It will automatically look for config in default locations
        cmd = [
            str(config.binary_path),
        ]
        
        if background:
            # Run in background thread
            self.thread = threading.Thread(target=self._run_background, args=(cmd,))
            self.thread.daemon = True
            self.thread.start()
        else:
            # Run in foreground
            self._run_foreground(cmd)
    
    def stop(self) -> None:
        """Stop SyftBox client."""
        if self.process and self.process.poll() is None:
            # Send SIGTERM for graceful shutdown
            self.process.terminate()
            
            # Wait up to 5 seconds for process to exit
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if not responsive
                self.process.kill()
                self.process.wait()
            
            self.process = None
    
    def restart(self, config: Config) -> None:
        """Restart SyftBox client."""
        self.stop()
        time.sleep(1)  # Brief pause before restart
        self.start(config)
    
    def is_running(self) -> bool:
        """Check if SyftBox client is running."""
        if self.process:
            return self.process.poll() is None
        
        # Also check for existing syftbox processes
        try:
            # Check for syftbox process (not "syftbox client")
            result = subprocess.run(
                ["pgrep", "-f", "syftbox"],
                capture_output=True,
                text=True,
            )
            # Make sure we found a real syftbox process, not just our pgrep command
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                # Filter out empty strings
                pids = [p for p in pids if p]
                return len(pids) > 0
            return False
        except Exception:
            return False
    
    def get_status(self) -> dict:
        """Get client status information."""
        return {
            "running": self.is_running(),
            "pid": self.process.pid if self.process else None,
        }
    
    def _run_foreground(self, cmd: list) -> None:
        """Run client in foreground."""
        try:
            self.process = subprocess.Popen(cmd)
            self.process.wait()
        except KeyboardInterrupt:
            self.stop()
    
    def _run_background(self, cmd: list) -> None:
        """Run client in background thread."""
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.process.wait()
        except Exception:
            pass


# Module-level functions for convenience
_launcher = Launcher()


def start_client(config: Optional[Config] = None, background: bool = False) -> None:
    """Start SyftBox client."""
    if not config:
        config = Config.load()
        if not config:
            raise ValueError("No configuration found. Run installer first.")
    
    _launcher.start(config, background)


def stop_client() -> None:
    """Stop SyftBox client."""
    _launcher.stop()


def restart_client(config: Optional[Config] = None) -> None:
    """Restart SyftBox client."""
    if not config:
        config = Config.load()
        if not config:
            raise ValueError("No configuration found. Run installer first.")
    
    _launcher.restart(config)


def is_running() -> bool:
    """Check if SyftBox client is running."""
    return _launcher.is_running()