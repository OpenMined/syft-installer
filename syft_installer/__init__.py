import os

from syft_installer.__version__ import __version__
from syft_installer.hybrid_installer import HybridInstaller as Installer
from syft_installer.programmatic_installer import ProgrammaticInstaller, install_programmatic
from syft_installer.config import load_config, is_installed
from syft_installer.launcher import start_client, stop_client, is_running


def install(**kwargs):
    """
    Quick install function for one-liner usage.
    
    Supports environment variables from install.sh:
    - INSTALL_MODE: interactive (default), download-only, setup-only
    - INSTALL_APPS: comma-separated list of apps to install
    - DEBUG: true/false for debug output
    - ARTIFACT_BASE_URL: base URL for downloads
    """
    # Check environment variables (matching install.sh)
    mode = os.environ.get("INSTALL_MODE", kwargs.get("install_mode", "interactive"))
    apps = os.environ.get("INSTALL_APPS", kwargs.get("install_apps"))
    debug = os.environ.get("DEBUG", str(kwargs.get("debug", False))).lower() in ("true", "1", "yes")
    base_url = os.environ.get("ARTIFACT_BASE_URL", kwargs.get("artifact_base_url", "https://syftbox.net"))
    
    # Update kwargs with env vars
    kwargs.update({
        "install_mode": mode,
        "install_apps": apps,
        "debug": debug,
        "artifact_base_url": base_url,
    })
    
    installer = Installer(**kwargs)
    return installer.install()


__all__ = [
    "__version__",
    "Installer",
    "ProgrammaticInstaller",
    "install",
    "install_programmatic",
    "load_config",
    "is_installed",
    "start_client",
    "stop_client",
    "is_running",
]