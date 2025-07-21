"""
Hybrid installer that combines install.sh approach with programmatic capabilities.
"""
import os
import subprocess
from pathlib import Path
from typing import Optional, Callable

from syft_installer.auth import Authenticator
from syft_installer.config import Config
from syft_installer.installer_v2 import InstallerV2
from syft_installer.runtime import RuntimeEnvironment
from syft_installer.utils import InputHandler, ProgressHandler


class HybridInstaller(InstallerV2):
    """
    Extends InstallerV2 to support programmatic authentication for notebooks/headless.
    
    This installer follows install.sh closely but provides fallback for environments
    where the TUI cannot run (notebooks, headless, etc).
    """
    
    def __init__(
        self,
        email: Optional[str] = None,
        server_url: str = "https://syftbox.net",
        data_dir: Optional[str] = None,
        install_mode: str = "interactive",
        install_apps: Optional[str] = None,
        debug: bool = False,
        artifact_base_url: str = "https://syftbox.net",
        headless: bool = False,
        otp_callback: Optional[Callable] = None,
        progress_callback: Optional[Callable] = None,
    ):
        # Initialize parent
        super().__init__(
            install_mode=install_mode,
            install_apps=install_apps,
            debug=debug,
            artifact_base_url=artifact_base_url,
            headless=headless,
        )
        
        # Additional attributes for programmatic mode
        self.email = email
        self.server_url = server_url
        self.data_dir = Path(data_dir).expanduser() if data_dir else Path(self.runtime.default_data_dir)
        self.otp_callback = otp_callback
        self.progress_callback = progress_callback
        
        # Components for programmatic auth
        self.auth = Authenticator(server_url)
        self.input_handler = InputHandler(self.runtime, headless)
        
        # Update progress handler with callback
        if progress_callback:
            self.progress = ProgressHandler(self.runtime, progress_callback)
    
    def _run_login(self) -> None:
        """
        Override login to support programmatic authentication in notebooks.
        """
        # First, try to run syftbox login if we're in a terminal
        if self.runtime.has_tty and not self.headless:
            try:
                super()._run_login()
                return
            except Exception as e:
                self._debug(f"Binary login failed: {e}, falling back to programmatic auth")
        
        # For notebooks/headless, use programmatic authentication
        self._programmatic_login()
    
    def _programmatic_login(self) -> None:
        """Handle authentication programmatically for notebook/headless environments."""
        self.progress.update("Starting programmatic authentication", 60)
        
        # Get email
        if not self.email:
            if self.headless:
                raise ValueError("Email required in headless mode")
            self.email = self.input_handler.get_input("Enter your email address: ")
        
        # Request OTP
        self.progress.update(f"Requesting OTP for {self.email}", 65)
        self.auth.request_otp(self.email)
        
        # Get OTP
        if self.otp_callback:
            otp = self.otp_callback()
        elif self.headless:
            raise ValueError("OTP callback required in headless mode")
        else:
            prompt = f"Enter the OTP sent to {self.email}: "
            otp = self.input_handler.get_input(prompt)
        
        # Verify OTP
        self.progress.update("Verifying OTP", 70)
        tokens = self.auth.verify_otp(self.email, otp)
        
        # Create configuration (matching what syftbox login would create)
        config = Config(
            email=self.email,
            server_url=self.server_url,
            data_dir=str(self.data_dir),
            refresh_token=tokens["refresh_token"],
        )
        config.save()
        
        self.progress.update("Authentication successful", 80)
    
    def authenticate(self) -> None:
        """Convenience method for programmatic authentication."""
        self._programmatic_login()
    
    def request_otp(self, email: Optional[str] = None) -> None:
        """Request OTP for programmatic flow."""
        email = email or self.email
        if not email:
            raise ValueError("Email is required")
        
        self.auth.request_otp(email)
        self.email = email
    
    def verify_otp(self, otp: str) -> dict:
        """Verify OTP for programmatic flow."""
        if not self.email:
            raise ValueError("Must call request_otp first")
        
        tokens = self.auth.verify_otp(self.email, otp)
        
        # Save configuration
        config = Config(
            email=self.email,
            server_url=self.server_url,
            data_dir=str(self.data_dir),
            refresh_token=tokens["refresh_token"],
        )
        config.save()
        
        return tokens
    
    def start_client(self, background: bool = True) -> None:
        """Start client with better control."""
        if background or self.runtime.is_notebook:
            # Start in background for notebooks
            cmd = [str(self.syftbox_binary_path), "client"]
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            self.progress.update("SyftBox client started in background", 95)
        else:
            # Run in foreground for terminal
            self._start_client()
    
    def stop_client(self) -> None:
        """Stop the client."""
        try:
            subprocess.run(["pkill", "-f", "syftbox client"], check=False)
            self.progress.update("SyftBox client stopped", 100)
        except Exception as e:
            self._debug(f"Failed to stop client: {e}")
    
    def is_installed(self) -> bool:
        """Check if SyftBox is installed."""
        return self.syftbox_binary_path.exists() and Config.load() is not None
    
    def is_running(self) -> bool:
        """Check if client is running."""
        return self._is_client_running()