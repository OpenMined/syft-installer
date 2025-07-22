"""
Consolidated utilities for syft-installer.

This module contains exceptions, validators, platform detection, and runtime utilities
that were previously split across multiple small modules.
"""
import os
import platform
import re
from email.utils import parseaddr
from typing import Optional, Tuple


# ============================================================================
# Exceptions
# ============================================================================

class SyftInstallerError(Exception):
    """Base exception for syft-installer."""
    pass


class PlatformError(SyftInstallerError):
    """Raised when platform is not supported."""
    pass


class DownloadError(SyftInstallerError):
    """Raised when download fails."""
    pass


class AuthenticationError(SyftInstallerError):
    """Raised when authentication fails."""
    pass


class ValidationError(SyftInstallerError):
    """Raised when input validation fails."""
    pass


class ConfigError(SyftInstallerError):
    """Raised when configuration operations fail."""
    pass


class BinaryNotFoundError(SyftInstallerError):
    """Raised when SyftBox binary is not found."""
    pass


# ============================================================================
# Validators
# ============================================================================

def validate_email(email: str) -> bool:
    r"""
    Validate email address.
    - Must pass RFC 5322 validation
    - Must match pattern: ^[^\s@]+@[^\s@]+\.[^\s@]+$
    """
    if not email:
        return False
    
    # RFC 5322 validation
    parsed = parseaddr(email)
    if not parsed[1] or parsed[1] != email:
        return False
    
    # Additional pattern validation
    pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    return bool(re.match(pattern, email))


def validate_otp(otp: str) -> bool:
    """
    Validate OTP code.
    - Must be exactly 8 characters
    - Must be uppercase alphanumeric only
    """
    if not otp:
        return False
    
    pattern = r"^[0-9A-Z]{8}$"
    return bool(re.match(pattern, otp))


def sanitize_otp(otp: str) -> str:
    """Convert OTP to uppercase and remove spaces."""
    return otp.strip().upper().replace(" ", "")


# ============================================================================
# Platform Detection
# ============================================================================

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
    
    # Binary naming convention: syftbox_client_{os}_{arch}.tar.gz
    binary_name = f"syftbox_client_{os_name}_{arch}"
    
    return f"{base_url}/releases/{binary_name}.tar.gz"


# ============================================================================
# Runtime Environment Detection
# ============================================================================

class RuntimeEnvironment:
    """Detect and adapt to different Python runtime environments."""
    
    def __init__(self):
        self._is_colab: Optional[bool] = None
    
    @property
    def is_colab(self) -> bool:
        """Check if running in Google Colab."""
        if self._is_colab is None:
            try:
                import google.colab
                self._is_colab = True
            except ImportError:
                self._is_colab = False
        return self._is_colab
    
    @property
    def default_data_dir(self) -> str:
        """Get default data directory based on environment."""
        if self.is_colab:
            # Use /content for Colab persistence
            return "/content/SyftBox"
        else:
            # Use home directory for regular environments
            return os.path.expanduser("~/SyftBox")