import platform
import sys
from typing import Tuple

from syft_installer.exceptions import PlatformError


def get_platform_info() -> Tuple[str, str]:
    """
    Detect OS and architecture.
    
    Returns:
        Tuple of (os_name, arch) where:
        - os_name: 'darwin' or 'linux'
        - arch: 'amd64' or 'arm64'
    
    Raises:
        PlatformError: If platform is not supported
    """
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # Map OS names
    if system == "darwin":
        os_name = "darwin"
    elif system == "linux":
        os_name = "linux"
    else:
        raise PlatformError(f"Unsupported operating system: {system}")
    
    # Map architecture names
    if machine in ["x86_64", "amd64"]:
        arch = "amd64"
    elif machine in ["arm64", "aarch64"]:
        arch = "arm64"
    else:
        raise PlatformError(f"Unsupported architecture: {machine}")
    
    return os_name, arch


def get_binary_url(base_url: str = "https://syftbox.net") -> str:
    """
    Get the download URL for the SyftBox binary based on platform.
    
    Args:
        base_url: Base URL for downloads
        
    Returns:
        Full URL to download the binary
    """
    os_name, arch = get_platform_info()
    
    # Binary naming convention: syftbox-{os}-{arch}
    binary_name = f"syftbox-{os_name}-{arch}"
    
    return f"{base_url}/binaries/{binary_name}.tar.gz"


def get_python_version() -> str:
    """Get Python version string."""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def check_python_version(min_version: str = "3.8") -> bool:
    """Check if Python version meets minimum requirement."""
    current = sys.version_info[:2]
    required = tuple(map(int, min_version.split(".")))
    return current >= required