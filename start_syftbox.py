#!/usr/bin/env python3
"""
Start SyftBox client manually.
"""

import syft_installer as si

# Check if installed
if not si.is_installed():
    print("❌ SyftBox is not installed. Run installation first.")
    exit(1)

# Check if already running
if si.is_running():
    print("✅ SyftBox is already running")
    exit(0)

# Start the client
print("🚀 Starting SyftBox client...")
try:
    si.start_client(background=True)
    print("✅ SyftBox client started successfully")
    print("\nTo check if it's running: si.is_running()")
    print("To stop it: si.stop_client()")
except Exception as e:
    print(f"❌ Failed to start: {e}")