# In your notebook, run this to start the client:

import syft_installer as si

# Check if installed
if not si.is_installed():
    print("SyftBox not installed")
else:
    # Check if running
    if si.is_running():
        print("✅ SyftBox is already running")
    else:
        print("🚀 Starting SyftBox client...")
        si.start_client(background=True)
        
        # Wait a moment for it to start
        import time
        time.sleep(2)
        
        # Check again
        if si.is_running():
            print("✅ SyftBox client started successfully!")
        else:
            print("❌ Client may have started but exited. Check logs.")
            print("Try running manually: ~/.local/bin/syftbox daemon")