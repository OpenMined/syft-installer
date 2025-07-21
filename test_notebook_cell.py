# Copy this code into a Jupyter notebook cell to test:

import syft_installer as si

# Method 1: Simple one-liner (will prompt for email and OTP)
# si.install()

# Method 2: Pre-configured with email (will only prompt for OTP)
email = "your.email@example.com"  # Replace with your email
installer = si.Installer(email=email)
installer.install()

# Method 3: Step by step for debugging
"""
import syft_installer as si

# Replace with your email
email = "your.email@example.com"
installer = si.Installer(email=email)

# Download binary
print("Downloading binary...")
installer.download_binary()
print("✅ Done")

# Setup environment
print("Setting up environment...")
installer.setup_environment()
print("✅ Done")

# Request OTP
print(f"Requesting OTP for {email}...")
installer.request_otp()
print("✅ Check your email!")

# After you get the OTP, run this:
otp = "ABCD1234"  # Replace with your OTP
installer.verify_otp(otp)
print("✅ Authenticated!")

# Start client
installer.start_client(background=True)
print("✅ SyftBox is running!")
"""