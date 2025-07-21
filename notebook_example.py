# Example: Fully Programmatic Installation in Jupyter Notebook

# Cell 1: Import and start installation
import syft_installer as si

# Create programmatic installer with your email
installer = si.install_programmatic("liamtrask@gmail.com")

# Request OTP (this will download binary and send OTP)
installer.install_step1_request_otp()

# Cell 2: Check status while waiting for email
installer.get_otp_status()

# Cell 3: Once you have the OTP from your email, verify it
otp = "38870126"  # Replace with your actual OTP
installer.install_step2_verify_otp(otp)

# Alternative: Step-by-step approach for more control
"""
import syft_installer as si

# Create installer
installer = si.ProgrammaticInstaller(email="liamtrask@gmail.com")

# Download binary
installer.download_binary()

# Setup environment
installer.setup_environment()

# Request OTP
installer.request_otp()
print("Check your email for OTP!")

# Verify OTP when ready
installer.verify_otp("38870126")

# Start client
installer.start_client(background=True)
"""