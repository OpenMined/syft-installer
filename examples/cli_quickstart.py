#!/usr/bin/env python3
"""
SyftBox CLI Quickstart

Run this script to install and start SyftBox:
    python cli_quickstart.py
"""

import syft_installer as si

def main():
    print("\n🚀 SyftBox Quickstart\n")
    
    # Check current status
    print("Checking status...")
    if si.is_installed():
        print("✅ SyftBox is installed")
        if si.is_running():
            print("✅ SyftBox is running")
        else:
            print("❌ SyftBox is not running")
    else:
        print("❌ SyftBox is not installed")
    
    # Show detailed status
    print("\nCurrent status:")
    si.status()
    
    # Offer to run SyftBox
    if not si.is_running():
        response = input("\nWould you like to start SyftBox? (y/n): ")
        if response.lower() == 'y':
            print("\nStarting SyftBox...")
            si.run()
            print("\n✅ SyftBox is now running!")
    else:
        print("\n✅ SyftBox is already running!")
        print("\nAvailable commands:")
        print("  si.stop()     - Stop the daemon")
        print("  si.restart()  - Restart the daemon")
        print("  si.status()   - Check status")

if __name__ == "__main__":
    main()