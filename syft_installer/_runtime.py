import os
import sys
from typing import Optional


class RuntimeEnvironment:
    """Detect and adapt to different Python runtime environments."""
    
    def __init__(self):
        self._is_notebook: Optional[bool] = None
        self._is_colab: Optional[bool] = None
        self._has_tty: Optional[bool] = None
        self._can_use_widgets: Optional[bool] = None
    
    @property
    def is_notebook(self) -> bool:
        """Check if running in a Jupyter notebook environment."""
        if self._is_notebook is None:
            try:
                from IPython import get_ipython
                shell = get_ipython()
                if shell is None:
                    self._is_notebook = False
                else:
                    self._is_notebook = (
                        hasattr(shell, 'kernel') or 
                        shell.__class__.__name__ in ['ZMQInteractiveShell', 'TerminalInteractiveShell']
                    )
            except ImportError:
                self._is_notebook = False
        return self._is_notebook
    
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
    def has_tty(self) -> bool:
        """Check if terminal is available for input."""
        if self._has_tty is None:
            self._has_tty = (
                hasattr(sys.stdin, 'isatty') and 
                sys.stdin.isatty() and 
                os.getenv('TERM') is not None
            )
        return self._has_tty
    
    @property
    def can_use_widgets(self) -> bool:
        """Check if ipywidgets can be used."""
        if self._can_use_widgets is None:
            if not self.is_notebook:
                self._can_use_widgets = False
            else:
                try:
                    import ipywidgets
                    from IPython.display import display
                    # Try to create and display a widget
                    test_widget = ipywidgets.Label("test")
                    display(test_widget)
                    self._can_use_widgets = True
                except Exception:
                    self._can_use_widgets = False
        return self._can_use_widgets
    
    @property
    def is_headless(self) -> bool:
        """Check if running in headless mode (no UI available)."""
        return not self.has_tty and not self.can_use_widgets
    
    @property
    def default_data_dir(self) -> str:
        """Get default data directory based on environment."""
        if self.is_colab:
            # Use /content for Colab persistence
            return "/content/SyftBox"
        else:
            # Use home directory for regular environments
            return os.path.expanduser("~/SyftBox")