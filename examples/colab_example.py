"""
Example usage of syft-installer in Google Colab with automatic email detection.

This example demonstrates:
1. Automatic email detection in Colab
2. Non-interactive mode for programmatic OTP submission
"""

import syft_installer as si

# Example 1: Interactive mode with auto email detection (Colab only)
# In Google Colab, this will automatically detect your email
# si.install_and_run()  # No email needed in Colab!

# Example 2: Non-interactive mode with auto email detection (Colab only)
# This is useful when building apps/services on top of syft-installer
def install_with_custom_otp_handler():
    """Example of non-interactive installation with custom OTP handling."""
    # In Colab, email will be auto-detected
    session = si.install_and_run(interactive=False)
    
    if session:
        print("Installation session started!")
        print("An OTP has been sent to your email.")
        
        # In a real app, you might:
        # - Show a form to collect the OTP
        # - Get it from an API endpoint
        # - Read it from a configuration file
        # etc.
        
        # For this example, we'll simulate getting it from somewhere
        otp = input("Please enter the OTP from your email: ")
        
        # Submit the OTP
        result = session.submit_otp(otp)
        
        if result.get("status") == "success":
            print("✅ Installation complete and SyftBox is running!")
        else:
            print(f"❌ Installation failed: {result.get('message')}")
    else:
        print("SyftBox is already installed or an error occurred")

# Example 3: Check if we're in Colab
from syft_installer._colab_utils import is_google_colab

if is_google_colab():
    print("🎉 Running in Google Colab! Email will be detected automatically.")
else:
    print("📍 Not in Colab. You'll need to provide your email manually.")

# Example 4: Standard usage (works everywhere)
# si.install_and_run("your-email@example.com")  # Works in Colab and elsewhere