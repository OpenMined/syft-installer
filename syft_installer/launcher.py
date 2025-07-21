import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Optional

from syft_installer.config import Config
from syft_installer.exceptions import BinaryNotFoundError


class Launcher:
    """Handle SyftBox client process management."""
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
    
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
        
        # Build command - run syftbox daemon to keep it running
        # It will automatically look for config in default locations
        cmd = [
            str(config.binary_path),
            "daemon",
        ]
        
        if background:
            # Start the process detached - no thread needed
            self._run_background(cmd)
        else:
            # Run in foreground
            self._run_foreground(cmd)
    
    def stop(self) -> None:
        """Stop SyftBox client."""
        # First try to stop our own process if we have one
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            except Exception:
                pass
            self.process = None
        
        # Also stop any other syftbox daemons
        try:
            # Use pkill to stop all syftbox daemon processes
            subprocess.run(["pkill", "-f", "syftbox daemon"], check=False)
        except Exception:
            # Fallback: try to find and kill manually
            try:
                result = subprocess.run(
                    ["pgrep", "-f", "syftbox daemon"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid:
                            try:
                                os.kill(int(pid), signal.SIGTERM)
                            except Exception:
                                pass
            except Exception:
                pass
    
    def restart(self, config: Config) -> None:
        """Restart SyftBox client."""
        self.stop()
        time.sleep(1)  # Brief pause before restart
        self.start(config)
    
    def is_running(self) -> bool:
        """Check if SyftBox client is running."""
        # Always check for external processes, not just our own
        try:
            # Check for syftbox daemon process
            result = subprocess.run(
                ["pgrep", "-f", "syftbox daemon"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                # Filter out empty strings and our own pgrep
                pids = [p for p in pids if p]
                return len(pids) > 0
            return False
        except Exception:
            # Fallback for systems without pgrep
            try:
                result = subprocess.run(
                    ["ps", "aux"],
                    capture_output=True,
                    text=True,
                )
                return "syftbox daemon" in result.stdout
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
            # Use nohup and detach from current process completely
            import platform
            if platform.system() == "Windows":
                # Windows doesn't have nohup, use START instead
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
                )
            else:
                # Unix-like systems: use nohup and full detachment
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True,
                    preexec_fn=os.setpgrp  # Detach from process group
                )
                # Don't wait - let it run independently
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