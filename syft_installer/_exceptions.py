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