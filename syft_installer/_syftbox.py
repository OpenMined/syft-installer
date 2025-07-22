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
from syft_installer._simple_installer import SimpleInstaller as _SimpleInstaller
from syft_installer._launcher import Launcher as _Launcher
from syft_installer._daemon_manager import DaemonManager as _DaemonManager


_console = Console()


class InstallerSession:
    """
    Non-interactive installation session for programmatic OTP submission.
    
    This class is returned when using install_and_run() or install() with 
    interactive=False, allowing you to submit the OTP programmatically.
    """
    
    def __init__(self, installer: '_SimpleInstaller', syftbox: '_SyftBox', background: bool = True):
        """
        Initialize installer session.
        
        Args:
            installer: The SimpleInstaller instance
            syftbox: The SyftBox instance  
            background: Whether to run in background after installation
        """
        self.installer = installer
        self.syftbox = syftbox
        self.background = background
        self._otp_sent = False
        self._installation_complete = False
        
    def request_otp(self) -> Dict[str, Any]:
        """
        Request OTP to be sent to the email address.
        
        Returns:
            Dict with status and message
        """
        result = self.installer.step1_download_and_request_otp()
        if result.get("status") == "success":
            self._otp_sent = True
        return result
        
    def submit_otp(self, otp: str) -> Dict[str, Any]:
        """
        Submit the OTP code to complete installation.
        
        Args:
            otp: The OTP code received via email
            
        Returns:
            Dict with status and message
        """
        if not self._otp_sent:
            return {
                "status": "error",
                "message": "OTP not requested yet. Call request_otp() first."
            }
            
        result = self.installer.step2_verify_otp(otp, start_client=False)
        
        if result.get("status") == "success":
            self._installation_complete = True
            _console.print("\n✅ Installation complete!")
            
            # Start the client if requested
            if self.background:
                config = self.syftbox.config
                if config:
                    _console.print("\n▶️  Starting SyftBox client...")
                    self.syftbox._launcher.start(config, background=True)
                    _console.print("✅ SyftBox client started!\n")
                    self.syftbox.status()
                    
        return result
        
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
        self._launcher = _Launcher()
        self._daemon_manager = _DaemonManager()
    
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
        result = self._launcher.is_running()
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
            status["daemons"] = self._daemon_manager.find_daemons()
        
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
            self._launcher.start(config, background=background)
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
            killed = self._daemon_manager.kill_all_daemons()
            _console.print(f"\n⏹️  Stopped {killed} SyftBox daemon(s)\n")
        else:
            self._launcher.stop()
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
        self._launcher.start(config, background=True)
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
        killed = self._daemon_manager.kill_all_daemons()
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
        
        installer = _SimpleInstaller(
            email=email,
            server_url=self.server
        )
        
        # Step 1: Download and request OTP
        result = installer.step1_download_and_request_otp()
        
        # Check if step 1 failed
        if result.get("status") == "error":
            _console.print(f"\n❌ Installation failed: {result.get('message', 'Unknown error')}")
            return
        
        # Step 2: Get OTP from user and verify
        otp = _console.input("\n📧 Enter the OTP sent to your email: ")
        result = installer.step2_verify_otp(otp, start_client=False)
        
        # Check if step 2 failed
        if result.get("status") == "error":
            _console.print(f"\n❌ Verification failed: {result.get('message', 'Unknown error')}")
            return
        
        _console.print("\n✅ Installation complete!")
    
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
                
            installer = _SimpleInstaller(
                email=self.email,
                server_url=self.server
            )
            
            session = InstallerSession(installer, self, background)
            
            # Request OTP
            result = session.request_otp()
            if result.get("status") == "error":
                _console.print(f"\n❌ Installation failed: {result.get('message', 'Unknown error')}")
                return None
                
            _console.print("\n📧 OTP sent! Check your email (including spam folder)")
            _console.print("👉 Use session.submit_otp('YOUR_OTP') to complete installation\n")
            
            return session
        else:
            # Already installed, just run if not running
            config = self.config
            if config:
                _console.print(f"✅ SyftBox already installed for [cyan]{config.email}[/cyan]")
                
            if not self.is_running:
                _console.print("\n▶️  Starting SyftBox client...")
                self._launcher.start(config, background=background)
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
        
        installer = _SimpleInstaller(
            email=email,
            server_url=instance.server
        )
        
        session = InstallerSession(installer, instance, background=False)
        
        # Request OTP
        result = session.request_otp()
        if result.get("status") == "error":
            _console.print(f"\n❌ Installation failed: {result.get('message', 'Unknown error')}")
            return None
            
        _console.print("\n📧 OTP sent! Check your email (including spam folder)")
        _console.print("👉 Use session.submit_otp('YOUR_OTP') to complete installation\n")
        
        return session


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
        instance._launcher.start(config, background=background)
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