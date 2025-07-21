# Simple SyftBox Installation Example for Jupyter Notebooks

# Cell 1: Import and create installer
import syft_installer as si

# Create simple installer with your email
installer = si.SimpleInstaller("liamtrask@gmail.com")

# Check current status
installer.get_status()

# Cell 2: Download binary and request OTP
result = installer.step1_download_and_request_otp()
print(result)

# Cell 3: After you receive the OTP email, verify it
# Replace with your actual OTP from email
otp = "38870126"
result = installer.step2_verify_otp(otp)
print(result)

# Cell 4: Check final status
installer.get_status()

# Optional: Stop/start client
# installer.stop_client()
# installer.start_client()