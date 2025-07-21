from syft_installer.__version__ import __version__
from syft_installer.installer import Installer
from syft_installer.config import load_config, is_installed
from syft_installer.launcher import start_client, stop_client, is_running


def install(**kwargs):
    """Quick install function for one-liner usage."""
    installer = Installer(**kwargs)
    return installer.install()


__all__ = [
    "__version__",
    "Installer",
    "install",
    "load_config",
    "is_installed",
    "start_client",
    "stop_client",
    "is_running",
]