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
        
        print(f"📌 Binary path: {config.binary_path}")
        print(f"📌 Command to execute: {cmd}")
        
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
        print("🔍 Checking if SyftBox is running...")
        try:
            # Check for syftbox daemon process
            result = subprocess.run(
                ["pgrep", "-f", "syftbox daemon"],
                capture_output=True,
                text=True,
            )
            print(f"   pgrep return code: {result.returncode}")
            print(f"   pgrep stdout: {repr(result.stdout)}")
            print(f"   pgrep stderr: {repr(result.stderr)}")
            
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                # Filter out empty strings and our own pgrep
                pids = [p for p in pids if p]
                print(f"   Found PIDs: {pids}")
                return len(pids) > 0
            print("   No processes found via pgrep")
            return False
        except Exception as e:
            print(f"   pgrep failed with exception: {e}")
            # Fallback for systems without pgrep
            try:
                print("   Trying ps aux fallback...")
                result = subprocess.run(
                    ["ps", "aux"],
                    capture_output=True,
                    text=True,
                )
                print(f"   ps aux return code: {result.returncode}")
                found = "syftbox daemon" in result.stdout
                if found:
                    # Print the matching lines
                    for line in result.stdout.split('\n'):
                        if 'syftbox' in line and 'grep' not in line:
                            print(f"   Found process: {line.strip()}")
                print(f"   Result: {'Found' if found else 'Not found'} via ps aux")
                return found
            except Exception as e2:
                print(f"   ps aux also failed: {e2}")
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
        print(f"🚀 Launching daemon with command: {' '.join(cmd)}")
        try:
            # Use nohup and detach from current process completely
            import platform
            system = platform.system()
            print(f"   Platform: {system}")
            
            if system == "Windows":
                # Windows doesn't have nohup, use START instead
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
                )
            else:
                # Unix-like systems: use nohup and full detachment
                # Create a temp file for stderr to debug issues
                import tempfile
                self.stderr_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, prefix='syftbox_stderr_')
                print(f"   Stderr will be logged to: {self.stderr_file.name}")
                
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=self.stderr_file,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True,
                    preexec_fn=os.setpgrp  # Detach from process group
                )
            
            print(f"   Process started with PID: {self.process.pid}")
            
            # Give it a moment to start
            print("   Waiting 2 seconds for daemon to initialize...")
            time.sleep(2)
            
            # Check if it started successfully
            poll_result = self.process.poll()
            if poll_result is not None:
                print(f"   ❌ Process exited with code: {poll_result}")
                # Read stderr to see what went wrong
                if hasattr(self, 'stderr_file'):
                    self.stderr_file.seek(0)
                    stderr_content = self.stderr_file.read()
                    print(f"   Stderr output: {stderr_content}")
                raise RuntimeError(f"SyftBox daemon failed to start (exit code: {poll_result})")
            else:
                print("   ✅ Process appears to be running")
                # Check stderr for any warnings
                if hasattr(self, 'stderr_file'):
                    self.stderr_file.seek(0)
                    stderr_content = self.stderr_file.read()
                    if stderr_content:
                        print(f"   ⚠️  Stderr output (non-fatal): {stderr_content}")
                # Don't wait - let it run independently
        except Exception as e:
            print(f"   ❌ Failed to start daemon: {e}")
            import traceback
            traceback.print_exc()
            raise


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