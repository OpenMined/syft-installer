"""Unified process management for SyftBox."""
import os
import signal
import subprocess
import tempfile
import time
from pathlib import Path
from typing import List, Dict, Optional

from syft_installer._exceptions import BinaryNotFoundError


class ProcessManager:
    """Manages SyftBox daemon processes - both starting and finding/killing."""
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.stderr_file = None
    
    def start(self, config, background: bool = True) -> None:
        """Start SyftBox client."""
        if self.is_running():
            return
        
        # Check binary exists
        if not config.binary_path.exists():
            raise BinaryNotFoundError(f"SyftBox binary not found at {config.binary_path}")
        
        # Build command
        cmd = [str(config.binary_path), "daemon"]
        
        print(f"📌 Binary path: {config.binary_path}")
        print(f"📌 Command to execute: {cmd}")
        
        if background:
            self._run_background(cmd)
        else:
            self._run_foreground(cmd)
    
    def stop(self) -> None:
        """Stop the SyftBox client we started."""
        if self.process and self.process.poll() is None:
            print("   Stopping process...")
            try:
                self.process.terminate()
                # Give it time to shutdown gracefully
                for _ in range(10):
                    if self.process.poll() is not None:
                        break
                    time.sleep(0.5)
                # Force kill if still running
                if self.process.poll() is None:
                    self.process.kill()
            except Exception:
                pass
        
        # Clean up stderr file
        if self.stderr_file and hasattr(self.stderr_file, 'name'):
            try:
                if os.path.exists(self.stderr_file.name):
                    # Try to read any errors before deleting
                    try:
                        with open(self.stderr_file.name, 'r') as f:
                            stderr_content = f.read().strip()
                            if stderr_content:
                                print(f"   Process stderr: {stderr_content}")
                    except:
                        pass
                    os.unlink(self.stderr_file.name)
            except:
                pass
    
    def is_running(self) -> bool:
        """Check if SyftBox client is running."""
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
                    for line in result.stdout.split('\n'):
                        if 'syftbox' in line and 'grep' not in line:
                            print(f"   Found process: {line.strip()}")
                print(f"   Result: {'Found' if found else 'Not found'} via ps aux")
                return found
            except Exception as e2:
                print(f"   ps aux also failed: {e2}")
                return False
    
    def find_daemons(self) -> List[Dict[str, str]]:
        """Find all running syftbox processes."""
        print("🔍 Looking for syftbox processes...")
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                check=True
            )
            
            processes = []
            lines = result.stdout.strip().split('\n')
            print(f"   Found {len(lines)-1} total processes")
            
            for line in lines[1:]:  # Skip header
                if 'syftbox' in line and 'grep' not in line:
                    print(f"   Syftbox process found: {line[:80]}...")
                    parts = line.split(None, 10)  # Split into max 11 parts
                    if len(parts) >= 11:
                        processes.append({
                            'user': parts[0],
                            'pid': parts[1],
                            'cpu': parts[2],
                            'mem': parts[3],
                            'start': parts[8],
                            'time': parts[9],
                            'command': parts[10]
                        })
            
            print(f"   Found {len(processes)} syftbox processes")
            return processes
        except Exception as e:
            print(f"   Error finding daemons: {e}")
            return []
    
    def kill_daemon(self, pid: str, force: bool = False) -> bool:
        """Kill a daemon process."""
        try:
            pid_int = int(pid)
            if force:
                os.kill(pid_int, signal.SIGKILL)
            else:
                os.kill(pid_int, signal.SIGTERM)
            return True
        except (ValueError, ProcessLookupError, PermissionError):
            return False
    
    def kill_all_daemons(self, force: bool = False) -> int:
        """Kill all syftbox daemons."""
        daemons = self.find_daemons()
        killed = 0
        
        for daemon in daemons:
            if self.kill_daemon(daemon['pid'], force):
                killed += 1
        
        return killed
    
    def _run_foreground(self, cmd: list) -> None:
        """Run client in foreground."""
        try:
            self.process = subprocess.Popen(cmd)
            self.process.wait()
        except KeyboardInterrupt:
            self.stop()
    
    def _run_background(self, cmd: list) -> None:
        """Run client in background."""
        print(f"🚀 Launching daemon with command: {' '.join(cmd)}")
        try:
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
                # Unix-like systems
                self.stderr_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, prefix='syftbox_stderr_')
                print(f"   Stderr will be logged to: {self.stderr_file.name}")
                
                # Check if we're in Google Colab
                in_colab = False
                try:
                    import google.colab
                    in_colab = True
                except ImportError:
                    pass
                
                if in_colab:
                    print("   ⚠️  Detected Google Colab environment - using simple subprocess")
                    # In Colab, use minimal subprocess options
                    self.process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=self.stderr_file,
                        stdin=subprocess.DEVNULL
                    )
                else:
                    # Regular Unix environment
                    self.process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=self.stderr_file,
                        stdin=subprocess.DEVNULL,
                        start_new_session=True,
                        preexec_fn=os.setsid
                    )
                
                # Give it a moment to start
                time.sleep(1)
                
                # Check if process started successfully
                if self.process.poll() is not None:
                    # Process died immediately
                    print("   ❌ Process failed to start!")
                    if self.stderr_file and os.path.exists(self.stderr_file.name):
                        with open(self.stderr_file.name, 'r') as f:
                            stderr_content = f.read().strip()
                            if stderr_content:
                                print(f"   Error output: {stderr_content}")
                    raise RuntimeError("Failed to start syftbox daemon")
                else:
                    print(f"   ✅ Process started with PID: {self.process.pid}")
                
        except Exception as e:
            print(f"   ❌ Failed to launch: {e}")
            # Clean up stderr file on error
            if self.stderr_file and hasattr(self.stderr_file, 'name'):
                try:
                    if os.path.exists(self.stderr_file.name):
                        os.unlink(self.stderr_file.name)
                except:
                    pass
            raise