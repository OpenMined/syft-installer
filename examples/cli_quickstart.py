#!/usr/bin/env python3
"""
SyftBox CLI Quickstart

Run this script to install and start SyftBox:
    python cli_quickstart.py
"""

import syftbox

def main():
    print("\n🚀 SyftBox Quickstart\n")
    
    # Check current status
    print("Checking status...")
    if syftbox.check.is_installed:
        print("✅ SyftBox is installed")
        if syftbox.check.is_running:
            print("✅ SyftBox is running")
        else:
            print("❌ SyftBox is not running")
    else:
        print("❌ SyftBox is not installed")
    
    # Show detailed status
    print("\nCurrent status:")
    syftbox.status()
    
    # Offer to run SyftBox
    if not syftbox.check.is_running:
        response = input("\nWould you like to start SyftBox? (y/n): ")
        if response.lower() == 'y':
            print("\nStarting SyftBox...")
            syftbox.run()
            print("\n✅ SyftBox is now running!")
    else:
        print("\n✅ SyftBox is already running!")
        print("\nAvailable commands:")
        print("  syftbox.stop()     - Stop the daemon")
        print("  syftbox.restart()  - Restart the daemon")
        print("  syftbox.status()   - Check status")

if __name__ == "__main__":
    main()