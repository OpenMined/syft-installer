"""Manage running SyftBox daemon processes."""
import subprocess
import signal
import os
from typing import List, Dict, Optional
from pathlib import Path


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
    
    def get_daemon_status(self, pid: str) -> Optional[Dict[str, str]]:
        """Get status of a specific daemon.
        
        Args:
            pid: Process ID to check
        
        Returns:
            Process info dict or None if not found
        """
        daemons = self.find_daemons()
        for daemon in daemons:
            if daemon['pid'] == pid:
                return daemon
        return None


def list_daemons() -> List[Dict[str, str]]:
    """List all running syftbox daemons."""
    manager = DaemonManager()
    return manager.find_daemons()


def kill_daemon(pid: str, force: bool = False) -> bool:
    """Kill a specific daemon."""
    manager = DaemonManager()
    return manager.kill_daemon(pid, force)


def kill_all_daemons(force: bool = False) -> int:
    """Kill all syftbox daemons."""
    manager = DaemonManager()
    return manager.kill_all_daemons(force)


def interactive_daemon_manager():
    """Interactive daemon management CLI."""
    manager = DaemonManager()
    
    while True:
        print("\n=== SyftBox Daemon Manager ===")
        daemons = manager.find_daemons()
        
        if not daemons:
            print("\nNo syftbox daemons found running.")
        else:
            print(f"\nFound {len(daemons)} syftbox daemon(s):\n")
            print(f"{'#':<3} {'PID':<8} {'USER':<12} {'CPU%':<6} {'MEM%':<6} {'START':<8} {'COMMAND'}")
            print("-" * 80)
            
            for i, daemon in enumerate(daemons, 1):
                cmd = daemon['command']
                if len(cmd) > 40:
                    cmd = cmd[:37] + "..."
                print(f"{i:<3} {daemon['pid']:<8} {daemon['user']:<12} "
                      f"{daemon['cpu']:<6} {daemon['mem']:<6} "
                      f"{daemon['start']:<8} {cmd}")
        
        print("\nOptions:")
        print("  1. Refresh list")
        print("  2. Kill a specific daemon")
        print("  3. Kill all daemons")
        print("  4. Force kill a specific daemon")
        print("  5. Force kill all daemons")
        print("  q. Quit")
        
        choice = input("\nEnter your choice: ").strip().lower()
        
        if choice == 'q':
            break
        elif choice == '1':
            continue
        elif choice == '2' and daemons:
            num = input("Enter daemon number to kill (or PID): ").strip()
            try:
                if num.isdigit() and 1 <= int(num) <= len(daemons):
                    daemon = daemons[int(num) - 1]
                    pid = daemon['pid']
                else:
                    pid = num
                
                if manager.kill_daemon(pid):
                    print(f"✓ Killed daemon {pid}")
                else:
                    print(f"✗ Failed to kill daemon {pid}")
            except Exception as e:
                print(f"✗ Error: {e}")
        elif choice == '3':
            killed = manager.kill_all_daemons()
            print(f"✓ Killed {killed} daemon(s)")
        elif choice == '4' and daemons:
            num = input("Enter daemon number to force kill (or PID): ").strip()
            try:
                if num.isdigit() and 1 <= int(num) <= len(daemons):
                    daemon = daemons[int(num) - 1]
                    pid = daemon['pid']
                else:
                    pid = num
                
                if manager.kill_daemon(pid, force=True):
                    print(f"✓ Force killed daemon {pid}")
                else:
                    print(f"✗ Failed to force kill daemon {pid}")
            except Exception as e:
                print(f"✗ Error: {e}")
        elif choice == '5':
            killed = manager.kill_all_daemons(force=True)
            print(f"✓ Force killed {killed} daemon(s)")
        else:
            print("Invalid choice")
        
        input("\nPress Enter to continue...")