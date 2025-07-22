"""
Simple programmatic installer for notebooks.
"""
import os
from pathlib import Path
from typing import Optional, Dict

from syft_installer._auth import Authenticator
from syft_installer._config import Config
from syft_installer._downloader import Downloader
from syft_installer._exceptions import ValidationError, BinaryNotFoundError
from syft_installer._launcher import Launcher
from syft_installer._platform import get_platform_info
from syft_installer._runtime import RuntimeEnvironment
from syft_installer._validators import validate_email, validate_otp, sanitize_otp


class SimpleInstaller:
    """
    Simple installer for programmatic use in notebooks.
    No inheritance complications - just straightforward methods.
    """
    
    def __init__(self, email: str, server_url: str = "https://syftbox.net"):
        """Initialize installer with email."""
        if not email:
            raise ValueError("Email is required")
        
        if not validate_email(email):
            raise ValidationError(f"Invalid email: {email}")
        
        self.email = email
        self.server_url = server_url
        self.runtime = RuntimeEnvironment()
        self.data_dir = Path(self.runtime.default_data_dir)
        
        # Component instances
        self.auth = Authenticator(server_url)
        self.downloader = Downloader()
        self.launcher = Launcher()
        
        # Paths
        self.bin_dir = Path.home() / ".local" / "bin"
        self.binary_path = self.bin_dir / "syftbox"
        self.config_dir = Path.home() / ".syftbox"
        self.config_file = self.config_dir / "config.json"
        
        # State
        self._otp_requested = False
    
    def step1_download_and_request_otp(self) -> Dict[str, str]:
        """
        Step 1: Download binary (if needed) and request OTP.
        
        Returns:
            Status dict with information about the step
        """
        print("🚀 Starting SyftBox installation...")
        
        # Debug runtime environment
        import platform
        print(f"🖥️  Platform: {platform.system()} {platform.release()}")
        print(f"🐍 Python: {platform.python_version()}")
        print(f"📁 Working directory: {os.getcwd()}")
        
        # Create directories
        self.bin_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Download binary if it doesn't exist
        if not self.binary_path.exists():
            print("📥 Downloading SyftBox binary...")
            try:
                self.downloader.download_and_install(self.binary_path)
                print("✅ Binary downloaded successfully")
            except Exception as e:
                print(f"❌ Download failed: {str(e)}")
                return {"status": "error", "message": f"Download failed: {str(e)}"}
        else:
            print("✅ Binary already exists")
        
        # Request OTP
        print(f"\n📧 Requesting OTP for {self.email}...")
        try:
            result = self.auth.request_otp(self.email)
            print(f"📧 OTP request response: {result}")
            self._otp_requested = True
            print("✅ OTP sent! Check your email (including spam folder)")
            print("\n👉 Next: Call step2_verify_otp('YOUR_OTP') with the code from your email")
            
            return {
                "status": "success", 
                "message": "OTP sent",
                "email": self.email,
                "next_step": "step2_verify_otp"
            }
        except Exception as e:
            print(f"❌ OTP request failed with error: {str(e)}")
            print(f"❌ Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": f"OTP request failed: {str(e)}"}
    
    def step2_verify_otp(self, otp: str, start_client: bool = True) -> Dict[str, str]:
        """
        Step 2: Verify OTP and complete installation.
        
        Args:
            otp: The 8-character OTP from email
            start_client: Whether to start the client after installation
            
        Returns:
            Status dict with installation results
        """
        if not self._otp_requested:
            return {"status": "error", "message": "Must call step1_download_and_request_otp first"}
        
        # Sanitize and validate OTP
        otp = sanitize_otp(otp)
        if not validate_otp(otp):
            return {"status": "error", "message": "Invalid OTP. Must be 8 uppercase alphanumeric characters."}
        
        print(f"🔐 Verifying OTP: {otp}")
        
        try:
            # Verify OTP and get tokens
            tokens = self.auth.verify_otp(self.email, otp)
            print("✅ Authentication successful")
            
            # Create and save config
            config = Config(
                email=self.email,
                data_dir=str(self.data_dir),
                server_url=self.server_url,
                client_url="http://localhost:7938",
                refresh_token=tokens["refresh_token"]
            )
            config.save()
            print("✅ Configuration saved")
            
            # Start client if requested
            if start_client:
                print("\n🚀 Starting SyftBox client...")
                self.launcher.start(config, background=True)
                print("✅ Client started in background")
            
            print("\n🎉 Installation complete!")
            print(f"📁 Data directory: {self.data_dir}")
            print(f"🔧 Config location: {self.config_file}")
            
            return {
                "status": "success",
                "message": "Installation complete",
                "data_dir": str(self.data_dir),
                "config_file": str(self.config_file),
                "client_running": start_client
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Verification failed: {str(e)}"}
    
    def get_status(self) -> Dict[str, any]:
        """Get current installation status."""
        return {
            "email": self.email,
            "otp_requested": self._otp_requested,
            "binary_exists": self.binary_path.exists(),
            "config_exists": self.config_file.exists(),
            "client_running": self.launcher.is_running()
        }
    
    def start_client(self) -> bool:
        """Start the SyftBox client if not already running."""
        if not self.config_file.exists():
            print("❌ No configuration found. Complete installation first.")
            return False
        
        if self.launcher.is_running():
            print("✅ Client is already running")
            return True
        
        config = Config.load()
        if config:
            print("🚀 Starting SyftBox client...")
            self.launcher.start(config, background=True)
            print("✅ Client started")
            return True
        
        return False
    
    def stop_client(self) -> bool:
        """Stop the SyftBox client."""
        if self.launcher.is_running():
            print("🛑 Stopping SyftBox client...")
            self.launcher.stop()
            print("✅ Client stopped")
            return True
        else:
            print("ℹ️  Client is not running")
            return False