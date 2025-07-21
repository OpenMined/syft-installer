"""
SyftBox - Dead simple API for managing SyftBox installation and execution.

Basic usage:
    import syftbox
    
    syftbox.run()     # Install (if needed) and start
    syftbox.status()  # Check status  
    syftbox.stop()    # Stop client
    syftbox.uninstall()  # Remove everything

That's it! The API is designed to be self-documenting through:
- Clear method names (run, stop, status, uninstall)
- Smart defaults (auto-install, background mode)
- Rich terminal output
- Helpful docstrings
"""

# Import everything from the main module
from syft_installer.syftbox import (
    status,
    run,
    stop,
    restart,
    uninstall,
    SyftBox
)

# Also expose the properties through a simple object
class _Properties:
    """Simple property access."""
    
    @property
    def is_installed(self) -> bool:
        """Is SyftBox installed?"""
        from syft_installer.syftbox import _get_instance
        return _get_instance().is_installed
    
    @property
    def is_running(self) -> bool:
        """Is SyftBox running?"""
        from syft_installer.syftbox import _get_instance
        return _get_instance().is_running
    
    @property
    def config(self):
        """Get current config."""
        from syft_installer.syftbox import _get_instance
        return _get_instance().config


# Create a single instance for property access
check = _Properties()

# Version
from syft_installer.__version__ import __version__

__all__ = [
    "status",
    "run", 
    "stop",
    "restart",
    "uninstall",
    "check",
    "SyftBox",
    "__version__"
]