"""
Fully programmatic installer for notebook environments.
"""
from typing import Optional

from syft_installer.hybrid_installer import HybridInstaller
from syft_installer.exceptions import ValidationError
from syft_installer.validators import validate_otp, sanitize_otp


class ProgrammaticInstaller(HybridInstaller):
    """
    Installer designed for fully programmatic usage in notebooks.
    No interactive prompts - all inputs must be provided programmatically.
    """
    
    def __init__(self, email: str, **kwargs):
        """
        Initialize programmatic installer.
        
        Args:
            email: Email address (required)
            **kwargs: Other installer options
        """
        if not email:
            raise ValueError("Email is required for programmatic installer")
        
        # Force headless mode for programmatic usage
        kwargs['headless'] = True
        super().__init__(email=email, **kwargs)
        
        self._otp_requested = False
        self._waiting_for_otp = False
    
    def install_step1_request_otp(self) -> None:
        """
        Step 1: Download binary and request OTP.
        Call this first to start the installation.
        """
        self.progress.update("Starting installation", 10)
        
        # Download binary
        self.progress.update("Downloading SyftBox binary", 20)
        self.download_binary()
        
        # Setup environment
        self.progress.update("Setting up environment", 40)
        self.setup_environment()
        
        # Request OTP
        self.progress.update(f"Requesting OTP for {self.email}", 60)
        self.request_otp()
        
        self._otp_requested = True
        self._waiting_for_otp = True
        
        self.progress.update("OTP sent! Check your email", 70)
        print(f"\n📧 OTP has been sent to {self.email}")
        print("Check your email (including spam folder)")
        print("\nNext: Call install_step2_verify_otp('YOUR_OTP') with the code from your email")
    
    def install_step2_verify_otp(self, otp: str, start_client: bool = True) -> None:
        """
        Step 2: Verify OTP and complete installation.
        
        Args:
            otp: The 8-character OTP from your email
            start_client: Whether to start the client after installation
        """
        if not self._otp_requested:
            raise ValueError("Must call install_step1_request_otp() first")
        
        if not self._waiting_for_otp:
            raise ValueError("OTP already verified or installation complete")
        
        # Sanitize and validate OTP
        otp = sanitize_otp(otp)
        if not validate_otp(otp):
            raise ValidationError("Invalid OTP. Must be 8 uppercase alphanumeric characters.")
        
        self.progress.update(f"Verifying OTP: {otp}", 75)
        
        # Verify OTP
        self.verify_otp(otp)
        
        self._waiting_for_otp = False
        self.progress.update("Authentication successful", 85)
        
        # Start client if requested
        if start_client:
            self.progress.update("Starting SyftBox client", 95)
            self.start_client(background=True)
        
        self.progress.update("Installation complete!", 100)
        print("\n✅ SyftBox installation complete!")
        print(f"📁 Data directory: {self.data_dir}")
        print(f"🔧 Config saved to: ~/.syftbox/config.json")
        
        if start_client:
            print("🚀 SyftBox client is running in the background")
        else:
            print("💡 To start the client later, run: installer.start_client()")
    
    def get_otp_status(self) -> dict:
        """Get the current OTP request status."""
        return {
            "otp_requested": self._otp_requested,
            "waiting_for_otp": self._waiting_for_otp,
            "email": self.email,
            "installed": self.is_installed(),
            "running": self.is_running() if self.is_installed() else False
        }


def install_programmatic(email: str) -> ProgrammaticInstaller:
    """
    Convenience function to create a programmatic installer.
    
    Usage:
        installer = install_programmatic("user@example.com")
        installer.install_step1_request_otp()
        # Check email for OTP
        installer.install_step2_verify_otp("ABCD1234")
    """
    return ProgrammaticInstaller(email=email)