"""Manage running SyftBox daemon processes."""
import subprocess
import signal
import os
from typing import List, Dict, Optional


class DaemonManager:
    """Manage SyftBox daemon processes."""
    
    def find_daemons(self) -> List[Dict[str, str]]:
        """Find all running syftbox processes.
        
        Returns:
            List of dicts with process info (pid, command, user)
        """
        print("🔍 DaemonManager: Looking for syftbox processes...")
        try:
            # Use ps to get detailed process info
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
        """Kill a daemon process.
        
        Args:
            pid: Process ID to kill
            force: Use SIGKILL instead of SIGTERM
        
        Returns:
            True if successful, False otherwise
        """
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
        """Kill all syftbox daemons.
        
        Args:
            force: Use SIGKILL instead of SIGTERM
        
        Returns:
            Number of processes killed
        """
        daemons = self.find_daemons()
        killed = 0
        
        for daemon in daemons:
            if self.kill_daemon(daemon['pid'], force):
                killed += 1
        
        return killed
    
