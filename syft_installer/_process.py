"""Unified process management for SyftBox."""
import os
import signal
import subprocess
import tempfile
import time
from pathlib import Path
from typing import List, Dict, Optional

from syft_installer._utils import BinaryNotFoundError


class ProcessManager:
    """Manages SyftBox daemon processes - both starting and finding/killing."""
    
    def __init__(self, verbose: bool = False):
        self.process: Optional[subprocess.Popen] = None
        self.stderr_file = None
        self.verbose = verbose
    
    def start(self, config, background: bool = True, progress_callback=None) -> Optional[int]:
        """Start SyftBox client. Returns PID if successful."""
        if self.is_running():
            return self.process.pid if self.process else None
        
        # Check binary exists
        if not config.binary_path.exists():
            raise BinaryNotFoundError(f"SyftBox binary not found at {config.binary_path}")
        
        # Build command
        cmd = [str(config.binary_path), "daemon"]
        
        if self.verbose:
            print(f"📌 Binary path: {config.binary_path}")
            print(f"📌 Command to execute: {cmd}")
        
        if background:
            self._run_background(cmd, progress_callback)
            return self.process.pid if self.process else None
        else:
            self._run_foreground(cmd)
            return None
    
    def stop(self) -> bool:
        """Stop the SyftBox client we started.
        
        Returns:
            True if a process was stopped, False otherwise
        """
        if self.process and self.process.poll() is None:
            # Only print if we actually have a process to stop
            if self.verbose:
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
                return True
            except Exception:
                pass
        return False
        
        # Clean up stderr file
        if self.stderr_file and hasattr(self.stderr_file, 'name'):
            try:
                if os.path.exists(self.stderr_file.name):
                    # Try to read any errors before deleting
                    try:
                        with open(self.stderr_file.name, 'r') as f:
                            stderr_content = f.read().strip()
                            if stderr_content and self.verbose:
                                print(f"   Process stderr: {stderr_content}")
                    except:
                        pass
                    os.unlink(self.stderr_file.name)
            except:
                pass
    
    def is_running(self) -> bool:
        """Check if SyftBox client is running."""
        if self.verbose:
            print("🔍 Checking if SyftBox is running...")
        
        try:
            # Check for syftbox daemon process
            result = subprocess.run(
                ["pgrep", "-f", "syftbox daemon"],
                capture_output=True,
                text=True,
            )
            
            if self.verbose:
                print(f"   pgrep return code: {result.returncode}")
                print(f"   pgrep stdout: {repr(result.stdout)}")
                print(f"   pgrep stderr: {repr(result.stderr)}")
            
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                pids = [p for p in pids if p]
                if self.verbose:
                    print(f"   Found PIDs: {pids}")
                return len(pids) > 0
            
            if self.verbose:
                print("   No processes found via pgrep")
            return False
            
        except Exception as e:
            if self.verbose:
                print(f"   pgrep failed with exception: {e}")
            
            # Fallback for systems without pgrep
            try:
                if self.verbose:
                    print("   Trying ps aux fallback...")
                
                result = subprocess.run(
                    ["ps", "aux"],
                    capture_output=True,
                    text=True,
                )
                
                if self.verbose:
                    print(f"   ps aux return code: {result.returncode}")
                
                found = "syftbox daemon" in result.stdout
                if found and self.verbose:
                    for line in result.stdout.split('\n'):
                        if 'syftbox' in line and 'grep' not in line:
                            print(f"   Found process: {line.strip()}")
                
                if self.verbose:
                    print(f"   Result: {'Found' if found else 'Not found'} via ps aux")
                
                return found
                
            except Exception as e2:
                if self.verbose:
                    print(f"   ps aux also failed: {e2}")
                return False
    
    def find_daemons(self) -> List[Dict[str, str]]:
        """Find all running syftbox processes."""
        if self.verbose:
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
            
            if self.verbose:
                print(f"   Found {len(lines)-1} total processes")
            
            for line in lines[1:]:  # Skip header
                if 'syftbox' in line and 'grep' not in line:
                    if self.verbose:
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
            
            if self.verbose:
                print(f"   Found {len(processes)} syftbox processes")
            
            return processes
            
        except Exception as e:
            if self.verbose:
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
    
    def _run_background(self, cmd: list, progress_callback=None) -> None:
        """Run client in background."""
        if self.verbose:
            print(f"🚀 Launching daemon with command: {' '.join(cmd)}")
        
        try:
            import platform
            system = platform.system()
            
            if self.verbose:
                print(f"   Platform: {system}")
            
            if progress_callback:
                progress_callback(70, f"🔧 Detected {system} environment")
            
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
                
                if self.verbose:
                    print(f"   Stderr will be logged to: {self.stderr_file.name}")
                
                # Check if we're in a restricted environment (Colab, Jupyter, etc.)
                restricted_env = False
                try:
                    import google.colab
                    restricted_env = True
                except ImportError:
                    # Test if preexec_fn works - it fails in some notebook environments
                    try:
                        # Quick test to see if preexec_fn works
                        test_proc = subprocess.Popen(
                            ['echo', 'test'], 
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL,
                            preexec_fn=lambda: None
                        )
                        test_proc.wait()
                    except (OSError, AttributeError, TypeError):
                        restricted_env = True
                
                if self.verbose and restricted_env:
                    print("   ⚠️  Detected restricted environment - using simple subprocess")
                
                if restricted_env:
                    # In restricted environments, use minimal subprocess options
                    self.process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=self.stderr_file,
                        stdin=subprocess.DEVNULL
                    )
                else:
                    # Regular Unix environment
                    # Check if we're in a Jupyter/IPython environment
                    in_jupyter = False
                    try:
                        get_ipython()  # This is defined in IPython/Jupyter
                        in_jupyter = True
                    except NameError:
                        pass
                    
                    if in_jupyter:
                        # Jupyter environment - use simpler subprocess call
                        self.process = subprocess.Popen(
                            cmd,
                            stdout=subprocess.DEVNULL,
                            stderr=self.stderr_file,
                            stdin=subprocess.DEVNULL
                        )
                    else:
                        # Regular terminal - try full daemon mode, fallback if needed
                        try:
                            self.process = subprocess.Popen(
                                cmd,
                                stdout=subprocess.DEVNULL,
                                stderr=self.stderr_file,
                                stdin=subprocess.DEVNULL,
                                start_new_session=True,
                                preexec_fn=os.setsid
                            )
                        except (OSError, subprocess.SubprocessError) as e:
                            if self.verbose:
                                print(f"   ⚠️  Full daemon mode failed ({e}), using simple mode")
                            # Fallback to simpler subprocess without preexec_fn
                            self.process = subprocess.Popen(
                                cmd,
                                stdout=subprocess.DEVNULL,
                                stderr=self.stderr_file,
                                stdin=subprocess.DEVNULL,
                                start_new_session=True
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
                    if progress_callback:
                        progress_callback(90, f"✅ Process started with PID: {self.process.pid}")
                    elif self.verbose:
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