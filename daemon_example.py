#!/usr/bin/env python3
"""
Example of using the daemon manager programmatically.
"""
import syft_installer as si


# List all running syftbox daemons
print("=== Listing SyftBox Daemons ===")
daemons = si.list_daemons()

if not daemons:
    print("No syftbox daemons found running.")
else:
    print(f"\nFound {len(daemons)} daemon(s):")
    for daemon in daemons:
        print(f"  PID: {daemon['pid']}, User: {daemon['user']}, Command: {daemon['command']}")

# Check if syftbox is running using the existing method
print(f"\nIs SyftBox running (via launcher): {si.is_running()}")

# Example of killing a specific daemon (commented out for safety)
# if daemons:
#     pid = daemons[0]['pid']
#     if si.kill_daemon(pid):
#         print(f"Killed daemon {pid}")

# Example of killing all daemons (commented out for safety)
# killed = si.kill_all_daemons()
# print(f"Killed {killed} daemons")