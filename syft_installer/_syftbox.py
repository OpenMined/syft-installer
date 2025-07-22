"""
Simple, intuitive API for SyftBox management.

Usage:
    import syft_installer as si
    
    # Install and run
    si.install_and_run("user@example.com")
    
    # Check status
    si.status()
    
    # Stop
    si.stop()
    
    # Uninstall completely
    si.uninstall()
"""
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any, Union
from rich.console import Console

from syft_installer._config import Config as _Config
from syft_installer._process import ProcessManager as _ProcessManager
from syft_installer._display import display
from syft_installer._progress import progress_context


_console = Console()


class InstallerSession:
    """
    Non-interactive installation session for programmatic OTP submission.
    
    This class is returned when using install_and_run() or install() with 
    interactive=False, allowing you to submit the OTP programmatically.
    """
    
    def __init__(self, email: str, syftbox: '_SyftBox', auth, background: bool = True):
        """
        Initialize installer session.
        
        Args:
            email: Email address for installation
            syftbox: The SyftBox instance  
            auth: Authenticator instance
            background: Whether to run in background after installation
        """
        self.email = email
        self.syftbox = syftbox
        self.auth = auth
        self.background = background
        self._otp_sent = True  # OTP is sent before creating session
        self._installation_complete = False
        
    def submit_otp(self, otp: str) -> Dict[str, Any]:
        """
        Submit the OTP code to complete installation.
        
        Args:
            otp: The OTP code received via email
            
        Returns:
            Dict with status and message
        """
        from syft_installer._utils import sanitize_otp, validate_otp
        
        # Sanitize and validate OTP
        otp = sanitize_otp(otp)
        if not validate_otp(otp):
            return {
                "status": "error",
                "message": "Invalid OTP. Must be 8 uppercase alphanumeric characters."
            }
        
        _console.print(f"🔐 Verifying OTP...")
        
        try:
            # Verify OTP and get tokens
            tokens = self.auth.verify_otp(self.email, otp)
            _console.print("✅ Authentication successful")
            
            # Create and save config
            config = _Config(
                email=self.email,
                data_dir=str(self.syftbox.data_dir),
                server_url=self.syftbox.server,
                client_url="http://localhost:7938",
                refresh_token=tokens["refresh_token"]
            )
            config.save()
            _console.print("✅ Configuration saved")
            
            self._installation_complete = True
            _console.print("\n✅ Installation complete!")
            
            # Start the client if requested
            if self.background:
                _console.print("\n▶️  Starting SyftBox client...")
                self.syftbox._process_manager.start(config, background=True)
                _console.print("✅ SyftBox client started!\n")
                self.syftbox.status()
            
            return {"status": "success", "message": "Installation complete"}
                    
        except Exception as e:
            return {"status": "error", "message": f"Verification failed: {str(e)}"}
        
    @property
    def is_complete(self) -> bool:
        """Check if installation is complete."""
        return self._installation_complete


class _SyftBox:
    """Dead simple SyftBox manager."""
    
    def __init__(self, 
                 email: Optional[str] = None,
                 server: str = "https://syftbox.net",
                 data_dir: Optional[str] = None):
        """
        Initialize SyftBox manager.
        
        Args:
            email: Your email (optional - will prompt if needed)
            server: SyftBox server URL (default: https://syftbox.net)
            data_dir: Data directory (default: ~/SyftBox)
        """
        self.email = email
        self.server = server
        self.data_dir = Path(data_dir).expanduser() if data_dir else Path.home() / "SyftBox"
        self._process_manager = _ProcessManager(verbose=False)
    
    @property
    def is_installed(self) -> bool:
        """Check if SyftBox is installed."""
        config = _Config.load()
        binary_path = Path.home() / ".local" / "bin" / "syftbox"
        return config is not None and binary_path.exists()
    
    @property
    def is_running(self) -> bool:
        """Check if SyftBox client is running."""
        return self._process_manager.is_running()
    
    @property
    def config(self) -> Optional[_Config]:
        """Get current configuration."""
        return _Config.load()
    
    def status(self, detailed: bool = False) -> Dict[str, Any]:
        """
        Get SyftBox status.
        
        Args:
            detailed: Show detailed information
            
        Returns:
            Status dictionary
        """
        status = {
            "installed": self.is_installed,
            "running": self.is_running,
            "config": None,
            "daemons": []
        }
        
        config = None
        if self.is_installed:
            config = self.config
            if config:
                status["config"] = {
                    "email": config.email,
                    "server": config.server_url,
                    "data_dir": config.data_dir
                }
        
        if detailed or self.is_running:
            status["daemons"] = self._process_manager.find_daemons()
        
        # Show clean status display
        display.show_status(
            installed=self.is_installed,
            running=self.is_running,
            email=config.email if config else None,
            data_dir=config.data_dir if config else None
        )
        
        return status
    
    def run(self, background: bool = True) -> None:
        """
        Install (if needed) and run SyftBox.
        
        This is the main entry point - it handles everything:
        1. Checks if installed
        2. Installs if needed (including OTP flow)
        3. Starts the client
        
        Args:
            background: Run client in background (default: True)
        """
        from syft_installer.__version__ import __version__
        
        # Show welcome message
        display.show_welcome(version=__version__)
        
        was_installed = self.is_installed
        
        if not was_installed:
            self._install()
        
        # Check configuration
        try:
            config = self.config
            if not config:
                display.show_error(
                    "Installation may have failed - no configuration found",
                    "Try running si.install() again or check your internet connection"
                )
                return
        except Exception as e:
            display.show_error(f"Error loading configuration: {e}")
            return
        
        # Start if not running
        if not self.is_running:
            # Only show progress if we didn't just install
            if was_installed:
                prog = progress_context()
                
                def progress_update(step, message):
                    prog.update(step, message)
                
                prog.update(20, f"🚀 Starting SyftBox daemon for {config.email}")
                prog.update(50, f"📌 Executing {config.binary_path} daemon")
                
                self._process_manager.start(config, background=background, progress_callback=progress_update)
                
                prog.update(95, "✅ SyftBox daemon started successfully")
                prog.finish(f"✅ SyftBox installed and running for {config.email}")
            else:
                # After fresh install, just start the daemon quietly
                self._process_manager.start(config, background=background)
                
                # Final status message
                print(f"✅ SyftBox is now running for {config.email}")
        else:
            display.show_already_running(config.email)
    
    def stop(self, all: bool = False) -> None:
        """
        Stop SyftBox client.
        
        Args:
            all: Stop all SyftBox daemons (not just the one we started)
        """
        if all:
            killed = self._process_manager.kill_all_daemons()
            _console.print(f"\n⏹️  Stopped {killed} SyftBox daemon(s)\n")
        else:
            self._process_manager.stop()
            _console.print("\n⏹️  Stopped SyftBox client\n")
    
    def start_if_stopped(self) -> bool:
        """
        Start SyftBox only if it's not already running.
        
        Returns:
            True if started, False if already running or not installed
        """
        if not self.is_installed:
            _console.print("❌ SyftBox not installed. Run .run() first.\n")
            return False
        
        if self.is_running:
            _console.print("✅ SyftBox already running!\n")
            return False
        
        _console.print("▶️  Starting SyftBox client...\n")
        config = self.config
        self._process_manager.start(config, background=True)
        _console.print("✅ SyftBox client started!\n")
        return True
    
    def uninstall(self, confirm: bool = True) -> None:
        """
        Completely uninstall SyftBox.
        
        This will:
        1. Stop all running daemons
        2. Delete ~/SyftBox directory
        3. Delete ~/.syftbox config
        4. Delete ~/.local/bin/syftbox binary
        
        Args:
            confirm: Ask for confirmation (default: True)
        """
        if confirm and not display.show_uninstall_warning():
            _console.print("❌ Uninstall cancelled.")
            return
        
        # Stop all daemons quietly
        self._process_manager.kill_all_daemons()
        
        # Delete directories and files
        paths_to_delete = [
            Path.home() / "SyftBox",
            Path.home() / ".syftbox",
            Path.home() / ".local" / "bin" / "syftbox"
        ]
        
        for path in paths_to_delete:
            if path.exists():
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                except Exception:
                    pass  # Silently continue if deletion fails
        
        display.show_uninstall_progress()
    
    def _install(self) -> None:
        """Run installation flow with single-line progress display."""
        # Auto-detect email in Colab if not provided
        email = self.email
        if email is None:
            from syft_installer._colab_utils import is_google_colab, get_colab_user_email
            
            if is_google_colab():
                email = get_colab_user_email()
                if email is None:
                    display.show_error(
                        "Could not detect your Google account email",
                        "Please provide your email explicitly: si.install('your@email.com')"
                    )
                    return
                self.email = email
            else:
                display.show_error(
                    "Email is required for installation",
                    "In Google Colab, we can detect it automatically. Otherwise, provide it: si.install('your@email.com')"
                )
                return
        
        # Validate email
        from syft_installer._utils import validate_email
        if not validate_email(email):
            display.show_error(f"Invalid email address: {email}")
            return
        
        # FIRST: Request OTP before doing anything else
        print(f"📧 Requesting verification code for {email}...")
        
        from syft_installer._auth import Authenticator
        auth = Authenticator(self.server)
        
        try:
            auth.request_otp(email)
        except Exception as e:
            display.show_error(f"Failed to request verification code: {str(e)}")
            return
        
        # Get OTP input
        otp = input("Enter Code from Email: ").strip()
        
        # Progress bar function
        def update_progress_bar(progress, width=50, message=""):
            """Update progress bar on the same line"""
            # Ensure progress is an integer
            progress = int(progress)
            filled = int(width * progress / 100)
            bar = '█' * filled + '░' * (width - filled)
            
            # For Jupyter, use \r to return to beginning of line
            sys.stdout.write('\r')
            
            # Write the progress bar
            if message:
                sys.stdout.write(f"{message} |{bar}| {progress:3.0f}%")
            else:
                sys.stdout.write(f"Progress: |{bar}| {progress:3.0f}%")
            
            sys.stdout.flush()
        
        # NOW: Start installation with smooth progress from 0 to 100
        try:
            # Phase 1: Setup (0-20%)
            for i in range(0, 21):
                update_progress_bar(i, message="📦 Setting up installation environment...")
                time.sleep(0.02)
            
            bin_dir = Path.home() / ".local" / "bin"
            binary_path = bin_dir / "syftbox"
            config_dir = Path.home() / ".syftbox"
            
            bin_dir.mkdir(parents=True, exist_ok=True)
            config_dir.mkdir(parents=True, exist_ok=True)
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
            # Phase 2: Download binary (20-50%)
            if not binary_path.exists():
                for i in range(21, 36):
                    update_progress_bar(i, message="📥 Downloading SyftBox binary...")
                    time.sleep(0.05)
                
                from syft_installer._downloader import Downloader
                downloader = Downloader()
                downloader.download_and_install(binary_path)
                
                for i in range(36, 51):
                    update_progress_bar(i, message="📥 Extracting SyftBox binary...")
                    time.sleep(0.03)
            else:
                for i in range(21, 51):
                    update_progress_bar(i, message="✅ SyftBox binary already exists")
                    time.sleep(0.01)
            
            # Phase 3: Verify OTP (50-80%)
            for i in range(51, 71):
                update_progress_bar(i, message="🔐 Verifying code...")
                time.sleep(0.03)
        
            from syft_installer._utils import sanitize_otp, validate_otp
            otp = sanitize_otp(otp)
            
            if not validate_otp(otp):
                sys.stdout.write("\r❌ Invalid verification code - must be 8 digits\n")
                sys.stdout.flush()
                return
            
            tokens = auth.verify_otp(email, otp)
            
            # Phase 4: Save configuration (70-90%)
            for i in range(71, 91):
                update_progress_bar(i, message="💾 Saving configuration...")
                time.sleep(0.02)
            
            config = _Config(
                email=email,
                data_dir=str(self.data_dir),
                server_url=self.server,
                client_url="http://localhost:7938",
                refresh_token=tokens["refresh_token"]
            )
            config.save()
            
            # Phase 5: Complete (90-100%)
            for i in range(91, 101):
                update_progress_bar(i, message="✅ Finalizing installation...")
                time.sleep(0.01)
            
            # Final message
            update_progress_bar(100, message="✅ SyftBox installation complete!")
            print()  # New line after progress bar
            
        except Exception as e:
            sys.stdout.write(f"\r❌ Installation failed: {str(e)}\n")
            sys.stdout.flush()
            return
    
    def _run_non_interactive(self, background: bool = True) -> Optional[InstallerSession]:
        """
        Run installation in non-interactive mode.
        
        Args:
            background: Run client in background after installation
            
        Returns:
            InstallerSession object if installation needed, None if already installed
        """
        from syft_installer.__version__ import __version__
        _console.print(f"\n[bold]🚀 Starting SyftBox... (syft-installer v{__version__})[/bold]\n")
        
        if not self.is_installed:
            _console.print("📦 SyftBox not installed. Starting installation...\n")
            
            # Auto-detect email in Colab if not provided
            if not self.email:
                from syft_installer._colab_utils import is_google_colab, get_colab_user_email
                
                if is_google_colab():
                    _console.print("🔍 Detected Google Colab environment")
                    self.email = get_colab_user_email()
                    if not self.email:
                        _console.print("❌ Could not detect email. Please provide it explicitly.")
                        return None
                else:
                    _console.print("❌ Email is required for non-interactive installation")
                    return None
                
            # Validate email
            from syft_installer._utils import validate_email
            if not validate_email(self.email):
                _console.print(f"❌ Invalid email address: {self.email}")
                return None
            
            # Create directories and download binary
            bin_dir = Path.home() / ".local" / "bin"
            binary_path = bin_dir / "syftbox"
            config_dir = Path.home() / ".syftbox"
            
            bin_dir.mkdir(parents=True, exist_ok=True)
            config_dir.mkdir(parents=True, exist_ok=True)
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
            # Download binary if needed
            if not binary_path.exists():
                _console.print("📥 Downloading SyftBox binary...")
                try:
                    from syft_installer._downloader import Downloader
                    downloader = Downloader()
                    downloader.download_and_install(binary_path)
                    _console.print("✅ Binary downloaded successfully")
                except Exception as e:
                    _console.print(f"❌ Download failed: {str(e)}")
                    return None
            else:
                _console.print("✅ Binary already exists")
            
            # Request OTP
            _console.print(f"\n📧 Requesting OTP for {self.email}...")
            try:
                from syft_installer._auth import Authenticator
                auth = Authenticator(self.server)
                result = auth.request_otp(self.email)
                _console.print("✅ OTP sent! Check your email (including spam folder)")
                
                session = InstallerSession(self.email, self, auth, background)
                _console.print("👉 Use session.submit_otp('YOUR_OTP') to complete installation\n")
                return session
                
            except Exception as e:
                _console.print(f"❌ OTP request failed: {str(e)}")
                return None
        else:
            # Already installed, just run if not running
            config = self.config
            if config:
                _console.print(f"✅ SyftBox already installed for [cyan]{config.email}[/cyan]")
                
            if not self.is_running:
                _console.print("\n▶️  Starting SyftBox client...")
                self._process_manager.start(config, background=background)
                _console.print("✅ SyftBox client started!\n")
            else:
                _console.print("✅ SyftBox client already running!\n")
                
            self.status()
            return None
    


# Module-level instance for super simple API
_instance = None


def _get_instance(**kwargs) -> _SyftBox:
    """Get or create the global SyftBox instance."""
    global _instance
    if _instance is None or kwargs:
        _instance = _SyftBox(**kwargs)
    return _instance


# Super simple API
def install(email: Optional[str] = None, interactive: bool = True) -> Union[bool, Optional[InstallerSession]]:
    """
    Install SyftBox without starting it.
    
    Downloads the binary and completes authentication via OTP.
    Useful when you want to install now but run later.
    
    Args:
        email: Your email address for authentication. If not provided in Google Colab,
               will attempt to detect it automatically from your Google account.
        interactive: If True, prompts for OTP input. If False, returns an InstallerSession
                    object for programmatic OTP submission (default: True)
        
    Returns:
        In interactive mode: True if installation successful, False otherwise
        In non-interactive mode: InstallerSession object or None if already installed
        
    Examples:
        Interactive mode:
        >>> import syft_installer as si
        >>> si.install("user@example.com")
        # Enter OTP when prompted
        >>> si.run()  # Start later
        
        Interactive mode in Colab (auto-detect email):
        >>> import syft_installer as si
        >>> si.install()  # Email detected from Google account
        
        Non-interactive mode:
        >>> import syft_installer as si
        >>> session = si.install("user@example.com", interactive=False)
        >>> if session:
        >>>     session.submit_otp("ABC12345")
        >>> si.run()  # Start later
    """
    # Auto-detect email in Colab if not provided
    if email is None:
        from syft_installer._colab_utils import is_google_colab, get_colab_user_email
        
        if is_google_colab():
            _console.print("🔍 Detected Google Colab environment")
            email = get_colab_user_email()
            if email is None:
                _console.print("❌ Could not detect email. Please provide it explicitly.")
                return False if interactive else None
        else:
            _console.print("❌ Email is required. In Google Colab, we can detect it automatically.")
            return False if interactive else None
    
    instance = _get_instance(email=email)
    if instance.is_installed:
        _console.print("✅ SyftBox is already installed")
        config = instance.config
        if config:
            _console.print(f"   Email: {config.email}")
        return True if interactive else None
    
    if interactive:
        _console.print("\n📦 Installing SyftBox...\n")
        instance._install()
        
        # Check if installation succeeded
        if instance.is_installed:
            _console.print("\n✅ Installation complete!")
            return True
        else:
            _console.print("\n❌ Installation failed")
            return False
    else:
        # Non-interactive mode
        _console.print("\n📦 Starting SyftBox installation...\n")
        
        # Validate email
        from syft_installer._utils import validate_email
        if not validate_email(email):
            _console.print(f"❌ Invalid email address: {email}")
            return None
        
        # Create directories and download binary
        bin_dir = Path.home() / ".local" / "bin"
        binary_path = bin_dir / "syftbox"
        config_dir = Path.home() / ".syftbox"
        
        bin_dir.mkdir(parents=True, exist_ok=True)
        config_dir.mkdir(parents=True, exist_ok=True)
        instance.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Download binary if needed
        if not binary_path.exists():
            _console.print("📥 Downloading SyftBox binary...")
            try:
                from syft_installer._downloader import Downloader
                downloader = Downloader()
                downloader.download_and_install(binary_path)
                _console.print("✅ Binary downloaded successfully")
            except Exception as e:
                _console.print(f"❌ Download failed: {str(e)}")
                return None
        else:
            _console.print("✅ Binary already exists")
        
        # Request OTP
        _console.print(f"\n📧 Requesting OTP for {email}...")
        try:
            from syft_installer._auth import Authenticator
            auth = Authenticator(instance.server)
            result = auth.request_otp(email)
            _console.print("✅ OTP sent! Check your email (including spam folder)")
            
            session = InstallerSession(email, instance, auth, background=False)
            _console.print("👉 Use session.submit_otp('YOUR_OTP') to complete installation\n")
            return session
            
        except Exception as e:
            _console.print(f"❌ OTP request failed: {str(e)}")
            return None


def run(background: bool = True) -> bool:
    """
    Run SyftBox (must be installed first).
    
    Starts the SyftBox daemon. Use install() first if not already installed.
    
    Args:
        background: Run daemon in background (default: True)
        
    Returns:
        True if started successfully, False otherwise
        
    Example:
        >>> import syft_installer as si
        >>> si.run()  # Assumes already installed
    """
    instance = _get_instance()
    
    if not instance.is_installed:
        _console.print("❌ SyftBox not installed. Run install() first.")
        return False
    
    if instance.is_running:
        _console.print("✅ SyftBox is already running")
        return True
    
    try:
        config = instance.config
        if not config:
            _console.print("❌ No configuration found")
            return False
            
        _console.print("▶️  Starting SyftBox client...")
        instance._process_manager.start(config, background=background)
        _console.print("✅ SyftBox client started!")
        return True
    except Exception as e:
        _console.print(f"❌ Failed to start: {e}")
        return False


def install_and_run_if_needed(email: Optional[str] = None, background: bool = True, interactive: bool = True) -> Optional['InstallerSession']:
    """
    Install (if needed) and run (if needed) SyftBox.
    
    This is the all-in-one function that handles everything:
    - Downloads and installs SyftBox binary if not installed
    - Handles email verification via OTP (only on first install)
    - Starts the SyftBox daemon in the background (only if not already running)
    
    Args:
        email: Your email address for authentication. Required on first install.
               Will prompt if not provided in interactive mode.
        background: Run daemon in background (default: True)
        interactive: If True, prompts for OTP input. If False, returns an InstallerSession
                    object for programmatic OTP submission (default: True)
        
    Returns:
        None in interactive mode, or InstallerSession object in non-interactive mode
        
    Examples:
        Interactive mode:
        >>> import syft_installer as si
        >>> si.install_and_run_if_needed("user@example.com")
        # Enter OTP when prompted
        
        Non-interactive mode:
        >>> import syft_installer as si
        >>> session = si.install_and_run_if_needed("user@example.com", interactive=False)
        >>> if session:
        >>>     session.submit_otp("ABC12345")
        
    Note:
        On first run, you'll receive an email with an 8-character OTP code.
        In interactive mode, enter this when prompted.
        In non-interactive mode, use the returned session object.
    """
    instance = _get_instance(email=email)
    
    if interactive:
        instance.run(background)
        return None
    else:
        # Non-interactive mode - return session for OTP submission
        return instance._run_non_interactive(background)


def status(detailed: bool = False) -> Dict[str, Any]:
    """
    Check SyftBox status.
    
    Shows whether SyftBox is installed, running, and configuration details.
    
    Args:
        detailed: Show detailed information including daemon processes
        
    Returns:
        Dict with status information
    
    Example:
        >>> import syft_installer as si
        >>> si.status()
        ╭─────── SyftBox Status ───────╮
        │ Installed  ✅ True           │
        │ Running    ✅ True           │
        │ Email      user@example.com  │
        │ Server     https://syftbox.net│
        │ Data Dir   /home/user/SyftBox│
        ╰──────────────────────────────╯
    """
    return _get_instance().status(detailed)




def stop(all: bool = False) -> None:
    """
    Stop SyftBox daemon.
    
    Args:
        all: Stop ALL syftbox daemons on the system, not just the one started
             by this instance (default: False)
        
    Example:
        >>> import syft_installer as si
        >>> si.stop()
    """
    _get_instance().stop(all)


def run_if_stopped() -> bool:
    """
    Start SyftBox only if it's not already running.
    
    Useful for ensuring SyftBox is running without restarting if already active.
    
    Returns:
        True if started, False if already running or not installed
        
    Example:
        >>> import syft_installer as si
        >>> si.run_if_stopped()
        ✅ SyftBox already running!
        False
    """
    return _get_instance().start_if_stopped()


def uninstall(confirm: bool = True) -> None:
    """
    Completely uninstall SyftBox.
    
    This will permanently delete:
    - ~/SyftBox (all your data and apps)
    - ~/.syftbox (configuration)  
    - ~/.local/bin/syftbox (binary)
    
    Args:
        confirm: Ask for confirmation before deleting (default: True).
                 Set to False for automated/scripted usage.
        
    Example:
        >>> import syft_installer as si
        >>> si.uninstall()
        
    Warning:
        This action cannot be undone. All data will be permanently deleted.
    """
    _get_instance().uninstall(confirm)