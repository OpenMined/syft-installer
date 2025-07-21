"""
Simple, intuitive API for SyftBox management.

Usage:
    import syftbox
    
    # Check status
    syftbox.status()
    
    # Install and start
    syftbox.run()
    
    # Stop
    syftbox.stop()
    
    # Uninstall completely
    syftbox.uninstall()
"""
import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from syft_installer.config import Config
from syft_installer.simple_installer import SimpleInstaller
from syft_installer.launcher import Launcher
from syft_installer.daemon_manager import DaemonManager


console = Console()


class SyftBox:
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
        self._launcher = Launcher()
        self._daemon_manager = DaemonManager()
    
    @property
    def is_installed(self) -> bool:
        """Check if SyftBox is installed."""
        config = Config.load()
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
    def config(self) -> Optional[Config]:
        """Get current configuration."""
        return Config.load()
    
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
        console.print("\n[bold]🚀 Starting SyftBox...[/bold]\n")
        
        if not self.is_installed:
            console.print("📦 SyftBox not installed. Installing now...\n")
            self._install()
        
        # Re-check after installation
        try:
            config = self.config
            if not config:
                console.print("❌ Installation may have failed - no configuration found")
                # Try to diagnose the issue
                config_file = Path.home() / ".syftbox" / "config.json"
                if config_file.exists():
                    console.print(f"Config file exists at {config_file}")
                    try:
                        with open(config_file, 'r') as f:
                            data = f.read()
                            console.print(f"Config content: {data[:200]}...")
                    except Exception as e:
                        console.print(f"Failed to read config: {e}")
                else:
                    console.print(f"Config file not found at {config_file}")
                return
            console.print(f"✅ SyftBox installed for [cyan]{config.email}[/cyan]")
        except Exception as e:
            console.print(f"❌ Error loading configuration: {e}")
            return
        
        if not self.is_running:
            console.print("\n▶️  Starting SyftBox client...")
            self._launcher.start(config, background=background)
            console.print("✅ SyftBox client started!\n")
        else:
            console.print("✅ SyftBox client already running!\n")
        
        self.status()
    
    def stop(self, all: bool = False) -> None:
        """
        Stop SyftBox client.
        
        Args:
            all: Stop all SyftBox daemons (not just the one we started)
        """
        if all:
            killed = self._daemon_manager.kill_all_daemons()
            console.print(f"\n⏹️  Stopped {killed} SyftBox daemon(s)\n")
        else:
            self._launcher.stop()
            console.print("\n⏹️  Stopped SyftBox client\n")
    
    def restart(self) -> None:
        """Restart SyftBox client."""
        console.print("\n🔄 Restarting SyftBox client...\n")
        config = self.config
        if config:
            self._launcher.restart(config)
            console.print("✅ SyftBox client restarted!\n")
        else:
            console.print("❌ SyftBox not installed. Run .run() first.\n")
    
    def start_if_stopped(self) -> bool:
        """
        Start SyftBox only if it's not already running.
        
        Returns:
            True if started, False if already running or not installed
        """
        if not self.is_installed:
            console.print("❌ SyftBox not installed. Run .run() first.\n")
            return False
        
        if self.is_running:
            console.print("✅ SyftBox already running!\n")
            return False
        
        console.print("▶️  Starting SyftBox client...\n")
        config = self.config
        self._launcher.start(config, background=True)
        console.print("✅ SyftBox client started!\n")
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
            console.print("\n[bold red]⚠️  WARNING: This will completely remove SyftBox![/bold red]")
            console.print("\nThis will delete:")
            console.print(f"  • [red]~/SyftBox[/red] (all your data)")
            console.print(f"  • [red]~/.syftbox[/red] (configuration)")
            console.print(f"  • [red]~/.local/bin/syftbox[/red] (binary)")
            console.print()
            
            response = console.input("Type 'yes' to confirm: ")
            if response.lower() != 'yes':
                console.print("\n❌ Uninstall cancelled.\n")
                return
        
        console.print("\n🗑️  Uninstalling SyftBox...\n")
        
        # Stop all daemons
        killed = self._daemon_manager.kill_all_daemons()
        if killed > 0:
            console.print(f"⏹️  Stopped {killed} daemon(s)")
        
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
                    console.print(f"🗑️  Deleted {path}")
                except Exception as e:
                    console.print(f"❌ Failed to delete {path}: {e}")
        
        console.print("\n✅ SyftBox uninstalled completely!\n")
    
    def _install(self) -> None:
        """Run installation flow."""
        installer = SimpleInstaller(
            email=self.email,
            server_url=self.server
        )
        
        # Step 1: Download and request OTP
        result = installer.step1_download_and_request_otp()
        
        # Check if step 1 failed
        if result.get("status") == "error":
            console.print(f"\n❌ Installation failed: {result.get('message', 'Unknown error')}")
            return
        
        # Step 2: Get OTP from user and verify
        otp = console.input("\n📧 Enter the OTP sent to your email: ")
        result = installer.step2_verify_otp(otp, start_client=False)
        
        # Check if step 2 failed
        if result.get("status") == "error":
            console.print(f"\n❌ Verification failed: {result.get('message', 'Unknown error')}")
            return
        
        console.print("\n✅ Installation complete!")
    
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
        
        # Config info
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
        console.print(panel)


# Module-level instance for super simple API
_instance = None


def _get_instance(**kwargs) -> SyftBox:
    """Get or create the global SyftBox instance."""
    global _instance
    if _instance is None or kwargs:
        _instance = SyftBox(**kwargs)
    return _instance


# Super simple API
def status(detailed: bool = False) -> Dict[str, Any]:
    """
    Check SyftBox status.
    
    Example:
        >>> import syftbox
        >>> syftbox.status()
        ╭─────── SyftBox Status ───────╮
        │ Installed  ✅ True           │
        │ Running    ✅ True           │
        │ Email      user@example.com  │
        │ Server     https://syftbox.net│
        │ Data Dir   /home/user/SyftBox│
        ╰──────────────────────────────╯
    """
    return _get_instance().status(detailed)


def run(email: Optional[str] = None, background: bool = True) -> None:
    """
    Install (if needed) and run SyftBox.
    
    This handles everything:
    - Installs SyftBox if not installed
    - Handles OTP authentication
    - Starts the client
    
    Args:
        email: Your email (optional - will prompt if needed)
        background: Run in background (default: True)
        
    Example:
        >>> import syftbox
        >>> syftbox.run()  # That's it!
    """
    instance = _get_instance(email=email)
    instance.run(background)


def stop(all: bool = False) -> None:
    """
    Stop SyftBox.
    
    Args:
        all: Stop ALL syftbox daemons (default: False)
        
    Example:
        >>> import syftbox
        >>> syftbox.stop()
    """
    _get_instance().stop(all)


def restart() -> None:
    """
    Restart SyftBox.
    
    Example:
        >>> import syftbox
        >>> syftbox.restart()
    """
    _get_instance().restart()


def start_if_stopped() -> bool:
    """
    Start SyftBox only if it's not already running.
    
    Returns:
        True if started, False if already running or not installed
        
    Example:
        >>> import syftbox
        >>> syftbox.start_if_stopped()
        ✅ SyftBox already running!
        False
    """
    return _get_instance().start_if_stopped()


def uninstall(confirm: bool = True) -> None:
    """
    Completely uninstall SyftBox.
    
    WARNING: This deletes:
    - ~/SyftBox (all data)
    - ~/.syftbox (config)  
    - ~/.local/bin/syftbox (binary)
    
    Args:
        confirm: Ask for confirmation (default: True)
        
    Example:
        >>> import syftbox
        >>> syftbox.uninstall()
    """
    _get_instance().uninstall(confirm)


# Properties for easy access
@property
def is_installed() -> bool:
    """Check if SyftBox is installed."""
    return _get_instance().is_installed


@property  
def is_running() -> bool:
    """Check if SyftBox is running."""
    return _get_instance().is_running


@property
def config() -> Optional[Config]:
    """Get current configuration."""
    return _get_instance().config