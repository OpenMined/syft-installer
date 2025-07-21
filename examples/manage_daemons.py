#!/usr/bin/env python3
"""
Manage SyftBox daemon processes.

Usage:
    python manage_daemons.py          # Interactive mode
    python manage_daemons.py list     # List all daemons
    python manage_daemons.py kill PID # Kill specific daemon
    python manage_daemons.py killall  # Kill all daemons
"""
import sys
import syft_installer as si


def main():
    """Main entry point."""
    if len(sys.argv) == 1:
        # Interactive mode
        si.interactive_daemon_manager()
    elif sys.argv[1] == "list":
        # List all daemons
        daemons = si.list_daemons()
        if not daemons:
            print("No syftbox daemons found.")
        else:
            print(f"Found {len(daemons)} daemon(s):\n")
            print(f"{'PID':<8} {'USER':<12} {'CPU%':<6} {'MEM%':<6} {'COMMAND'}")
            print("-" * 60)
            for d in daemons:
                cmd = d['command'][:40] + "..." if len(d['command']) > 40 else d['command']
                print(f"{d['pid']:<8} {d['user']:<12} {d['cpu']:<6} {d['mem']:<6} {cmd}")
    elif sys.argv[1] == "kill" and len(sys.argv) > 2:
        # Kill specific daemon
        pid = sys.argv[2]
        force = "--force" in sys.argv or "-f" in sys.argv
        if si.kill_daemon(pid, force):
            print(f"✓ Killed daemon {pid}")
        else:
            print(f"✗ Failed to kill daemon {pid}")
    elif sys.argv[1] == "killall":
        # Kill all daemons
        force = "--force" in sys.argv or "-f" in sys.argv
        killed = si.kill_all_daemons(force)
        print(f"✓ Killed {killed} daemon(s)")
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()