#!/usr/bin/env python3
"""
Demo of the super simple SyftBox API.

This shows how the API is self-documenting through:
1. Clear, intuitive naming
2. Smart defaults
3. Rich output
4. Minimal required parameters
"""

# That's it! This is all you need:
import syftbox

# Check if installed/running
print("\n1. Checking status...")
print(f"   Installed: {syftbox.check.is_installed}")
print(f"   Running: {syftbox.check.is_running}")

# See detailed status
print("\n2. Getting status...")
syftbox.status()

# The main magic - install and run with one line!
# (Commented out to avoid actually running)
# print("\n3. Running SyftBox...")
# syftbox.run()

# Other simple operations:
# syftbox.stop()      # Stop it
# syftbox.restart()   # Restart it  
# syftbox.uninstall() # Remove everything

# The API is so simple it barely needs documentation:
# - run(): Install (if needed) and start
# - stop(): Stop the client
# - status(): Show current status
# - restart(): Restart the client
# - uninstall(): Remove everything
# - check.is_installed: Property to check if installed
# - check.is_running: Property to check if running

print("\n✨ The entire API fits on a napkin!")
print("\nKey principles:")
print("- One-line install and run: syftbox.run()")
print("- Clear verbs: run, stop, status, uninstall")
print("- Smart defaults: auto-install, background mode")
print("- Rich output: beautiful status displays")
print("- Zero configuration needed for 99% of users")