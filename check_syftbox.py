#!/usr/bin/env python3
"""
Check if SyftBox is running and diagnose any issues.
"""

import subprocess
import os
from pathlib import Path
import syft_installer as si

def check_process():
    """Check if syftbox process is running."""
    print("=== Checking for SyftBox Process ===\n")
    
    # Method 1: Using ps
    try:
        result = subprocess.run(
            ["ps", "aux"], 
            capture_output=True, 
            text=True
        )
        syftbox_processes = [line for line in result.stdout.split('\n') if 'syftbox' in line.lower() and 'grep' not in line]
        
        if syftbox_processes:
            print("✅ Found SyftBox processes:")
            for proc in syftbox_processes:
                print(f"   {proc}")
        else:
            print("❌ No SyftBox process found using 'ps aux'")
    except Exception as e:
        print(f"❌ Error checking with ps: {e}")
    
    # Method 2: Using pgrep
    try:
        result = subprocess.run(
            ["pgrep", "-l", "syftbox"], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            print(f"\n✅ Found with pgrep: {result.stdout.strip()}")
        else:
            print("\n❌ No process found with pgrep")
    except Exception as e:
        print(f"\n❌ Error checking with pgrep: {e}")
    
    # Method 3: Check specific port
    print("\n=== Checking Port 7938 (SyftBox default) ===")
    try:
        result = subprocess.run(
            ["lsof", "-i", ":7938"], 
            capture_output=True, 
            text=True
        )
        if result.stdout:
            print(f"✅ Port 7938 in use:\n{result.stdout}")
        else:
            print("❌ Port 7938 not in use")
    except Exception as e:
        print(f"❌ Error checking port: {e}")

def check_files():
    """Check if SyftBox files exist."""
    print("\n=== Checking SyftBox Files ===\n")
    
    # Check binary
    binary_path = Path.home() / ".local" / "bin" / "syftbox"
    if binary_path.exists():
        print(f"✅ Binary exists: {binary_path}")
        # Check if executable
        if os.access(binary_path, os.X_OK):
            print("   ✅ Binary is executable")
        else:
            print("   ❌ Binary is NOT executable")
    else:
        print(f"❌ Binary NOT found at: {binary_path}")
    
    # Check config
    config_path = Path.home() / ".syftbox" / "config.json"
    if config_path.exists():
        print(f"\n✅ Config exists: {config_path}")
        # Read and display config (without sensitive data)
        try:
            import json
            with open(config_path) as f:
                config = json.load(f)
            print(f"   Email: {config.get('email', 'N/A')}")
            print(f"   Server: {config.get('server_url', 'N/A')}")
            print(f"   Data dir: {config.get('data_dir', 'N/A')}")
            print(f"   Has refresh token: {'refresh_token' in config}")
        except Exception as e:
            print(f"   ❌ Error reading config: {e}")
    else:
        print(f"❌ Config NOT found at: {config_path}")
    
    # Check data directory
    data_dir = Path.home() / "SyftBox"
    if data_dir.exists():
        print(f"\n✅ Data directory exists: {data_dir}")
    else:
        print(f"\n❌ Data directory NOT found at: {data_dir}")

def try_start_client():
    """Try to start the client manually."""
    print("\n=== Trying to Start Client Manually ===\n")
    
    binary_path = Path.home() / ".local" / "bin" / "syftbox"
    if not binary_path.exists():
        print("❌ Cannot start - binary not found")
        return
    
    print(f"Running: {binary_path} client")
    
    try:
        # Try to start in background
        proc = subprocess.Popen(
            [str(binary_path), "client"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )
        
        # Wait a moment to see if it starts
        import time
        time.sleep(2)
        
        if proc.poll() is None:
            print("✅ Client started successfully (PID: {})".format(proc.pid))
        else:
            stdout, stderr = proc.communicate()
            print("❌ Client exited immediately")
            if stdout:
                print(f"STDOUT: {stdout.decode()}")
            if stderr:
                print(f"STDERR: {stderr.decode()}")
            
    except Exception as e:
        print(f"❌ Error starting client: {e}")

def check_with_library():
    """Check using the syft_installer library."""
    print("\n=== Checking with syft_installer Library ===\n")
    
    print(f"Is installed: {si.is_installed()}")
    print(f"Is running: {si.is_running()}")
    
    config = si.load_config()
    if config:
        print(f"Config loaded: {config.email}")

def main():
    print("SyftBox Diagnostic Tool")
    print("=" * 50)
    
    check_files()
    check_process()
    check_with_library()
    
    # Ask if we should try to start
    print("\n" + "=" * 50)
    response = input("\nTry to start the client manually? [y/N]: ").strip().lower()
    if response == 'y':
        try_start_client()
        # Check again
        print("\n=== Checking Again After Start Attempt ===")
        check_process()

if __name__ == "__main__":
    main()