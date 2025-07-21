# Simple SyftBox API - Perfect for Notebooks!
# 
# Just three lines to get started:

import syftbox

# 1. Check current status
syftbox.status()

# 2. Run SyftBox (installs if needed, handles auth, starts client)
# syftbox.run()  # <-- Uncomment this to run!

# 3. That's it! You're done!

# Other useful commands:
# syftbox.stop()       # Stop the client
# syftbox.restart()    # Restart the client  
# syftbox.uninstall()  # Remove everything (careful!)

# Quick checks:
print(f"\nInstalled: {syftbox.check.is_installed}")
print(f"Running: {syftbox.check.is_running}")

# Advanced usage (only if you need custom settings):
# syftbox.run(email="custom@email.com")  # Specify email upfront

# Custom configuration (for the <1% who need it):
# custom = syftbox.SyftBox(
#     email="user@example.com",
#     server="https://custom.server.com", 
#     data_dir="/custom/path"
# )
# custom.run()