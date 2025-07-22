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
from pathlib import Path
from typing import Optional, Dict, Any, Union
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from syft_installer._config import Config as _Config
from syft_installer._process import ProcessManager as _ProcessManager


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
        self._process_manager = _ProcessManager()
    
    @property
    def is_installed(self) -> bool:
        """Check if SyftBox is installed."""
        config = _Config.load()
        binary_path = Path.home() / ".local" / "bin" / "syftbox"
        return config is not None and binary_path.exists()
    
    @property
    def is_running(self) -> bool:
        """Check if SyftBox client is running."""
        print("\n📊 Checking SyftBox running status...")
        result = self._process_manager.is_running()
        print(f"📊 Result: {result}\n")
        return result
    
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
        
        if self.is_installed:
            config = self.config
            status["config"] = {
                "email": config.email,
                "server": config.server_url,
                "data_dir": config.data_dir
            }
        
        if detailed or self.is_running:
            status["daemons"] = self._process_manager.find_daemons()
        
        # Pretty print status
        self._print_status(status)
        
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
        _console.print(f"\n[bold]🚀 Starting SyftBox... (syft-installer v{__version__})[/bold]\n")
        
        if not self.is_installed:
            _console.print("📦 SyftBox not installed. Installing now...\n")
            self._install()
        
        # Re-check after installation
        try:
            config = self.config
            if not config:
                _console.print("❌ Installation may have failed - no configuration found")
                # Try to diagnose the issue
                config_file = Path.home() / ".syftbox" / "config.json"
                if config_file.exists():
                    _console.print(f"_Config file exists at {config_file}")
                    try:
                        with open(config_file, 'r') as f:
                            data = f.read()
                            _console.print(f"_Config content: {data[:200]}...")
                    except Exception as e:
                        _console.print(f"Failed to read config: {e}")
                else:
                    _console.print(f"_Config file not found at {config_file}")
                return
            _console.print(f"✅ SyftBox installed for [cyan]{config.email}[/cyan]")
        except Exception as e:
            _console.print(f"❌ Error loading configuration: {e}")
            return
        
        if not self.is_running:
            _console.print("\n▶️  Starting SyftBox client...")
            self._process_manager.start(config, background=background)
            _console.print("✅ SyftBox client started!\n")
        else:
            _console.print("✅ SyftBox client already running!\n")
        
        self.status()
    
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
        if confirm:
            _console.print("\n[bold red]⚠️  WARNING: This will completely remove SyftBox![/bold red]")
            _console.print("\nThis will delete:")
            _console.print(f"  • [red]~/SyftBox[/red] (all your data)")
            _console.print(f"  • [red]~/.syftbox[/red] (configuration)")
            _console.print(f"  • [red]~/.local/bin/syftbox[/red] (binary)")
            _console.print()
            
            response = _console.input("Type 'yes' to confirm: ")
            if response.lower() != 'yes':
                _console.print("\n❌ Uninstall cancelled.\n")
                return
        
        _console.print("\n🗑️  Uninstalling SyftBox...\n")
        
        # Stop all daemons
        killed = self._process_manager.kill_all_daemons()
        if killed > 0:
            _console.print(f"⏹️  Stopped {killed} daemon(s)")
        
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
                    _console.print(f"🗑️  Deleted {path}")
                except Exception as e:
                    _console.print(f"❌ Failed to delete {path}: {e}")
        
        _console.print("\n✅ SyftBox uninstalled completely!\n")
    
    def _install(self) -> None:
        """Run installation flow."""
        # Auto-detect email in Colab if not provided
        email = self.email
        if email is None:
            from syft_installer._colab_utils import is_google_colab, get_colab_user_email
            
            if is_google_colab():
                _console.print("🔍 Detected Google Colab environment")
                email = get_colab_user_email()
                if email is None:
                    _console.print("❌ Could not detect email. Please provide it explicitly.")
                    return
                self.email = email  # Store for later use
            else:
                _console.print("❌ Email is required. In Google Colab, we can detect it automatically.")
                return
        
        # Validate email
        from syft_installer._utils import validate_email
        if not validate_email(email):
            _console.print(f"❌ Invalid email address: {email}")
            return
        
        _console.print("🚀 Starting SyftBox installation...")
        
        # Create directories
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
                return
        else:
            _console.print("✅ Binary already exists")
        
        # Request OTP
        _console.print(f"\n📧 Requesting OTP for {email}...")
        try:
            from syft_installer._auth import Authenticator
            auth = Authenticator(self.server)
            result = auth.request_otp(email)
            _console.print("✅ OTP sent! Check your email (including spam folder)")
        except Exception as e:
            _console.print(f"❌ OTP request failed: {str(e)}")
            return
        
        # Get OTP from user
        otp = _console.input("\n📧 Enter the OTP sent to your email: ")
        
        # Verify OTP
        from syft_installer._utils import sanitize_otp, validate_otp
        otp = sanitize_otp(otp)
        if not validate_otp(otp):
            _console.print("❌ Invalid OTP. Must be 8 uppercase alphanumeric characters.")
            return
        
        _console.print(f"🔐 Verifying OTP...")
        
        try:
            # Verify OTP and get tokens
            tokens = auth.verify_otp(email, otp)
            _console.print("✅ Authentication successful")
            
            # Create and save config
            from syft_installer._utils import RuntimeEnvironment
            config = _Config(
                email=email,
                data_dir=str(self.data_dir),
                server_url=self.server,
                client_url="http://localhost:7938",
                refresh_token=tokens["refresh_token"]
            )
            config.save()
            _console.print("✅ Configuration saved")
            
            _console.print("\n✅ Installation complete!")
            _console.print(f"📁 Data directory: {self.data_dir}")
            
        except Exception as e:
            _console.print(f"❌ Verification failed: {str(e)}")
    
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
    
    def _print_status(self, status: Dict[str, Any]) -> None:
        """Pretty print status information."""
        # Create status table
        table = Table(show_header=False, box=box.SIMPLE)
        table.add_column("Property", style="cyan")
        table.add_column("Value")
        
        # Basic status
        installed_icon = "✅" if status["installed"] else "❌"
        running_icon = "✅" if status["running"] else "❌"
        
        table.add_row("Installed", f"{installed_icon} {status['installed']}")
        table.add_row("Running", f"{running_icon} {status['running']}")
        
        # _Config info
        if status["config"]:
            table.add_row("Email", status["config"]["email"])
            table.add_row("Server", status["config"]["server"])
            table.add_row("Data Dir", status["config"]["data_dir"])
        
        # Daemon info
        if status["daemons"]:
            daemon_count = len(status["daemons"])
            pids = ", ".join(d["pid"] for d in status["daemons"])
            table.add_row("Daemons", f"{daemon_count} running (PIDs: {pids})")
        
        # Print in a nice panel
        panel = Panel(table, title="[bold]SyftBox Status[/bold]", border_style="green")
        _console.print(panel)


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


def install_and_run(email: Optional[str] = None, background: bool = True, interactive: bool = True) -> Optional['InstallerSession']:
    """
    Install (if needed) and run SyftBox.
    
    This is the all-in-one function that handles everything:
    - Downloads and installs SyftBox binary if not installed
    - Handles email verification via OTP
    - Starts the SyftBox daemon in the background
    
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
        >>> si.install_and_run("user@example.com")
        # Enter OTP when prompted
        
        Non-interactive mode:
        >>> import syft_installer as si
        >>> session = si.install_and_run("user@example.com", interactive=False)
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