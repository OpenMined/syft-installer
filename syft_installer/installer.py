import os
import sys
from pathlib import Path
from typing import Callable, Optional

from syft_installer.auth import Authenticator
from syft_installer.config import Config, load_config
from syft_installer.downloader import Downloader
from syft_installer.exceptions import HeadlessError, ValidationError
from syft_installer.launcher import Launcher
from syft_installer.runtime import RuntimeEnvironment
from syft_installer.utils import InputHandler, ProgressHandler
from syft_installer.validators import validate_email


class Installer:
    """Main installer class for SyftBox."""
    
    def __init__(
        self,
        email: Optional[str] = None,
        server_url: str = "https://syftbox.net",
        data_dir: Optional[str] = None,
        headless: bool = False,
        progress_callback: Optional[Callable] = None,
        otp_callback: Optional[Callable] = None,
    ):
        self.runtime = RuntimeEnvironment()
        self.headless = headless
        
        # Set data directory
        if data_dir:
            self.data_dir = Path(data_dir).expanduser()
        else:
            self.data_dir = Path(self.runtime.default_data_dir)
        
        self.email = email
        self.server_url = server_url
        self.progress_callback = progress_callback
        self.otp_callback = otp_callback
        
        # Initialize components
        self.auth = Authenticator(server_url)
        self.downloader = Downloader()
        self.launcher = Launcher()
        self.input_handler = InputHandler(self.runtime, self.headless)
        self.progress = ProgressHandler(self.runtime, progress_callback)
        
        # Load existing config if available
        self.config = load_config()
    
    def install(self) -> bool:
        """
        Run full installation process.
        
        Returns:
            True if installation successful
        """
        try:
            self.progress.update("Starting SyftBox installation", 0)
            
            # Check if already installed
            if self.is_installed():
                self.progress.update("SyftBox is already installed", 100)
                return True
            
            # Download and install binary
            self.progress.update("Downloading SyftBox binary", 20)
            self.download_binary()
            
            # Setup environment
            self.progress.update("Setting up environment", 40)
            self.setup_environment()
            
            # Authenticate
            self.progress.update("Starting authentication", 60)
            self.authenticate()
            
            # Start client (optional)
            if not self.headless:
                start_msg = "Start SyftBox client now? [Y/n]: "
                if self.input_handler.get_bool(start_msg, default=True):
                    self.progress.update("Starting SyftBox client", 90)
                    self.start_client()
            
            self.progress.update("Installation complete!", 100)
            return True
            
        except Exception as e:
            self.progress.error(f"Installation failed: {str(e)}")
            raise
    
    def download_binary(self) -> None:
        """Download and install SyftBox binary."""
        binary_path = Path.home() / ".local" / "bin" / "syftbox"
        self.downloader.download_and_install(binary_path)
    
    def setup_environment(self) -> None:
        """Setup environment (PATH, directories, etc)."""
        # Create data directory
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create config directory
        config_dir = Path.home() / ".syftbox"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Add to PATH if needed
        bin_dir = Path.home() / ".local" / "bin"
        if str(bin_dir) not in os.environ.get("PATH", ""):
            self._add_to_path(bin_dir)
    
    def authenticate(self) -> None:
        """Handle authentication flow."""
        # Check if we have valid existing credentials
        if self.config and self.config.is_valid():
            if not self.auth.is_token_expired(self.config.refresh_token):
                self.progress.update("Using existing credentials", 70)
                return
        
        # Get email
        if not self.email:
            self.email = self._get_email()
        
        # Request OTP
        self.progress.update(f"Requesting OTP for {self.email}", 65)
        self.request_otp()
        
        # Get OTP
        otp = self._get_otp()
        
        # Verify OTP
        self.progress.update("Verifying OTP", 75)
        tokens = self.verify_otp(otp)
        
        # Save configuration
        self.config = Config(
            email=self.email,
            server_url=self.server_url,
            data_dir=str(self.data_dir),
            refresh_token=tokens["refresh_token"],
        )
        self.config.save()
        self.progress.update("Authentication successful", 80)
    
    def request_otp(self, email: Optional[str] = None) -> None:
        """Request OTP to be sent to email."""
        email = email or self.email
        if not email:
            raise ValueError("Email is required")
        
        self.auth.request_otp(email)
        self.email = email
    
    def verify_otp(self, otp: str) -> dict:
        """Verify OTP and save tokens."""
        if not self.email:
            raise ValueError("Must call request_otp first")
        
        return self.auth.verify_otp(self.email, otp)
    
    def start_client(self, background: bool = False) -> None:
        """Start SyftBox client."""
        if not self.config:
            raise ValueError("Must authenticate first")
        
        self.launcher.start(self.config, background=background)
    
    def stop_client(self) -> None:
        """Stop SyftBox client."""
        self.launcher.stop()
    
    def is_installed(self) -> bool:
        """Check if SyftBox is installed."""
        binary_path = Path.home() / ".local" / "bin" / "syftbox"
        return binary_path.exists() and self.config is not None
    
    def is_running(self) -> bool:
        """Check if SyftBox client is running."""
        return self.launcher.is_running()
    
    def _get_email(self) -> str:
        """Get email from user."""
        while True:
            email = self.input_handler.get_input("Enter your email address: ")
            if validate_email(email):
                return email
            self.progress.error("Invalid email address")
    
    def _get_otp(self) -> str:
        """Get OTP from user or callback."""
        if self.otp_callback:
            return self.otp_callback()
        
        prompt = f"Enter the OTP sent to {self.email}: "
        return self.input_handler.get_input(prompt)
    
    def _add_to_path(self, bin_dir: Path) -> None:
        """Add directory to PATH."""
        # This is informational only - actual PATH modification
        # needs to be done in shell profile
        shell = os.environ.get("SHELL", "").split("/")[-1]
        profile_files = {
            "bash": "~/.bashrc",
            "zsh": "~/.zshrc",
            "fish": "~/.config/fish/config.fish",
        }
        
        if shell in profile_files:
            profile = profile_files[shell]
            self.progress.info(
                f"Add this to your {profile}: export PATH=\"$HOME/.local/bin:$PATH\""
            )