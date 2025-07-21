"""
Installer v2 - Closely follows install.sh implementation.
"""
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, List

from syft_installer.config import Config, load_config
from syft_installer.downloader import Downloader
from syft_installer.exceptions import BinaryNotFoundError, PlatformError
from syft_installer.platform import get_platform_info
from syft_installer.runtime import RuntimeEnvironment
from syft_installer.utils import ProgressHandler


class InstallerV2:
    """
    SyftBox installer that closely follows install.sh implementation.
    """
    
    def __init__(
        self,
        install_mode: str = "interactive",  # download-only, setup-only, interactive
        install_apps: Optional[str] = None,  # comma-separated app list
        debug: bool = False,
        artifact_base_url: str = "https://syftbox.net",
        headless: bool = False,
    ):
        self.install_mode = install_mode
        self.install_apps = install_apps.split(",") if install_apps else []
        self.debug = debug
        self.artifact_base_url = artifact_base_url
        self.headless = headless
        
        # Set up paths (matching install.sh)
        self.syftbox_dir = Path.home() / ".local" / "bin"
        self.syftbox_binary_path = self.syftbox_dir / "syftbox"
        self.app_name = "syftbox"
        
        # Initialize components
        self.runtime = RuntimeEnvironment()
        self.downloader = Downloader()
        self.progress = ProgressHandler(self.runtime)
        
        if self.debug:
            self._debug("Debug mode enabled")
            self._debug(f"Install mode: {self.install_mode}")
            self._debug(f"Install apps: {self.install_apps}")
    
    def install(self) -> bool:
        """Run installation following install.sh flow."""
        try:
            # Step 1: Download binary (unless setup-only mode)
            if self.install_mode != "setup-only":
                self._download_binary()
            
            # Step 2: Setup (unless download-only mode)
            if self.install_mode != "download-only":
                self._setup()
            
            return True
            
        except Exception as e:
            self.progress.error(f"Installation failed: {str(e)}")
            raise
    
    def _download_binary(self) -> None:
        """Download and extract binary (matches download_binary() from install.sh)."""
        self._debug("Starting binary download")
        
        # Get platform info
        os_name, arch = get_platform_info()
        pkg_name = f"{self.app_name}_client_{os_name}_{arch}"
        
        # Create directory
        self.syftbox_dir.mkdir(parents=True, exist_ok=True)
        
        # Download URL
        url = f"{self.artifact_base_url}/releases/{pkg_name}.tar.gz"
        self._debug(f"Download URL: {url}")
        
        # Download and install
        self.progress.update("Downloading SyftBox binary", 30)
        self.downloader.download_and_install(self.syftbox_binary_path)
        
        self.progress.update("Binary downloaded successfully", 50)
    
    def _setup(self) -> None:
        """Setup SyftBox (matches setup() from install.sh)."""
        self._debug("Starting setup")
        
        # Add to PATH
        self._add_to_path()
        
        # Remove old installations
        self._uninstall_old_versions()
        
        # Run syftbox login if interactive mode
        if self.install_mode == "interactive" and not self.headless:
            self._run_login()
        
        # Install apps if specified
        if self.install_apps:
            self._install_apps()
        
        # Prompt to start client (interactive mode only)
        if self.install_mode == "interactive" and not self.headless:
            self._prompt_start_client()
    
    def _run_login(self) -> None:
        """Run syftbox login command (delegates to binary)."""
        if not self.syftbox_binary_path.exists():
            raise BinaryNotFoundError(f"SyftBox binary not found at {self.syftbox_binary_path}")
        
        self.progress.update("Starting login process", 60)
        
        # Run syftbox login --quiet
        cmd = [str(self.syftbox_binary_path), "login", "--quiet"]
        self._debug(f"Running: {' '.join(cmd)}")
        
        try:
            # For notebooks/headless, we need to handle this differently
            if self.runtime.is_notebook or self.headless:
                # In notebooks, we can't run interactive TUI
                # Fall back to programmatic approach
                self.progress.error("Interactive login not supported in notebook/headless mode")
                self.progress.info("Please use programmatic authentication instead")
                return
            
            # Run the login command
            result = subprocess.run(cmd, check=True)
            
            if result.returncode == 0:
                self.progress.update("Login successful", 80)
            else:
                raise Exception("Login failed")
                
        except subprocess.CalledProcessError as e:
            raise Exception(f"Login failed: {str(e)}")
    
    def _install_apps(self) -> None:
        """Install apps using syftbox app install command."""
        if not self.syftbox_binary_path.exists():
            raise BinaryNotFoundError(f"SyftBox binary not found at {self.syftbox_binary_path}")
        
        for app in self.install_apps:
            self.progress.update(f"Installing app: {app}", 85)
            cmd = [str(self.syftbox_binary_path), "app", "install", app]
            self._debug(f"Running: {' '.join(cmd)}")
            
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                self.progress.update(f"Installed app: {app}", 90)
            except subprocess.CalledProcessError as e:
                self.progress.error(f"Failed to install app {app}: {e.stderr}")
    
    def _prompt_start_client(self) -> None:
        """Prompt user to start client (interactive mode)."""
        # Check if already running
        if self._is_client_running():
            self.progress.info("SyftBox client is already running")
            return
        
        # In headless/notebook mode, don't prompt
        if self.headless or self.runtime.is_notebook:
            return
        
        # Prompt user
        response = input("\nStart SyftBox client now? [Y/n]: ")
        if response.lower() != 'n':
            self._start_client()
    
    def _start_client(self) -> None:
        """Start SyftBox client."""
        cmd = [str(self.syftbox_binary_path), "client"]
        self._debug(f"Running: {' '.join(cmd)}")
        
        # Start in background
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.progress.update("SyftBox client started", 100)
    
    def _is_client_running(self) -> bool:
        """Check if client is already running."""
        try:
            result = subprocess.run(
                ["pgrep", "-f", "syftbox client"],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _add_to_path(self) -> None:
        """Add ~/.local/bin to PATH in shell profiles."""
        bin_dir = self.syftbox_dir
        
        # Check if already in PATH
        if str(bin_dir) in os.environ.get("PATH", ""):
            self._debug("~/.local/bin already in PATH")
            return
        
        # Determine shell and profile file
        shell = os.environ.get("SHELL", "").split("/")[-1]
        profile_files = {
            "bash": Path.home() / ".bashrc",
            "zsh": Path.home() / ".zshrc",
            "fish": Path.home() / ".config" / "fish" / "config.fish",
        }
        
        if shell not in profile_files:
            self.progress.info(f"Please add {bin_dir} to your PATH manually")
            return
        
        profile_file = profile_files[shell]
        
        # Check if already added
        if profile_file.exists():
            content = profile_file.read_text()
            if "/.local/bin" in content:
                self._debug(f"PATH already configured in {profile_file}")
                return
        
        # Add to profile
        self._debug(f"Adding {bin_dir} to PATH in {profile_file}")
        
        # Create parent directory if needed
        profile_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Append PATH export
        with open(profile_file, "a") as f:
            f.write(f'\n# Added by syft-installer\nexport PATH="$HOME/.local/bin:$PATH"\n')
        
        self.progress.info(f"Added {bin_dir} to PATH in {profile_file}")
        self.progress.info("Please restart your shell or run: source " + str(profile_file))
    
    def _uninstall_old_versions(self) -> None:
        """Remove old syftbox installations."""
        # Try to uninstall via uv
        try:
            subprocess.run(
                ["uv", "pip", "uninstall", "syftbox", "-y"],
                capture_output=True,
                check=False
            )
            self._debug("Uninstalled old syftbox via uv")
        except FileNotFoundError:
            # uv not found, try pip
            try:
                subprocess.run(
                    ["pip", "uninstall", "syftbox", "-y"],
                    capture_output=True,
                    check=False
                )
                self._debug("Uninstalled old syftbox via pip")
            except FileNotFoundError:
                self._debug("Neither uv nor pip found, skipping old version removal")
    
    def _debug(self, message: str) -> None:
        """Print debug message if debug mode is enabled."""
        if self.debug:
            print(f"[DEBUG] {message}")


# Convenience functions matching install.sh behavior
def install_syftbox(
    mode: str = "interactive",
    apps: Optional[str] = None,
    debug: bool = False,
) -> bool:
    """
    Install SyftBox following install.sh implementation.
    
    Args:
        mode: Installation mode (interactive, download-only, setup-only)
        apps: Comma-separated list of apps to install
        debug: Enable debug output
    
    Returns:
        True if installation successful
    """
    # Check environment variables (matching install.sh)
    mode = os.environ.get("INSTALL_MODE", mode)
    apps = os.environ.get("INSTALL_APPS", apps)
    debug = os.environ.get("DEBUG", str(debug)).lower() in ("true", "1", "yes")
    base_url = os.environ.get("ARTIFACT_BASE_URL", "https://syftbox.net")
    
    installer = InstallerV2(
        install_mode=mode,
        install_apps=apps,
        debug=debug,
        artifact_base_url=base_url,
    )
    
    return installer.install()