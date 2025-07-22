import os
from typing import Optional


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