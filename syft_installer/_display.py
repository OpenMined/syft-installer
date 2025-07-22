"""
Clean, progress-driven display system for syft-installer.

This module provides a polished user experience with progress bars,
temporary status updates, and inspiring messaging designed to create
a great first impression of the Syft ecosystem.
"""
import time
from contextlib import contextmanager
from typing import Optional, Iterator

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box


class SyftDisplay:
    """Clean, inspiring display system for SyftBox installation."""
    
    def __init__(self):
        self.console = Console()
        self._current_progress: Optional[Progress] = None
        self._current_live: Optional[Live] = None
    
    @contextmanager
    def installation_progress(self, email: str) -> Iterator[object]:
        """Show clean installation progress with inspiring messaging."""
        
        class ProgressContext:
            def update_phase(self, description: str, percent: int):
                """Update the current phase with clean messaging."""
                pass  # Silent progress
            
            def show_downloading(self, total_bytes: int) -> int:
                """Show download progress and return task ID."""
                return 0  # Silent download
            
            def update_download(self, task_id: int, completed: int):
                """Update download progress."""
                pass  # Silent update
            
            def complete_download(self, task_id: int):
                """Complete download phase."""
                pass  # Silent completion
        
        yield ProgressContext()
    
    def show_welcome(self, version: str):
        """Show inspiring welcome message."""
        pass  # Silent welcome
    
    def show_email_detection(self, email: str, is_colab: bool = False):
        """Show clean email detection message."""
        pass  # Silent email detection
    
    def show_otp_request(self, email: str):
        """Show clean OTP request message."""
        self.console.print(f"📧 Verification code sent to {email}")
    
    def get_otp_input(self) -> str:
        """Get OTP input with clean prompt."""
        return self.console.input("🔐 Enter your 8-digit verification code: ")
    
    def show_success(self, email: str, data_dir: str):
        """Show inspiring success message."""
        self.console.print(f"✅ SyftBox installed and running for {email}")
    
    def show_already_running(self, email: str):
        """Show message when SyftBox is already running."""
        self.console.print(f"✅ SyftBox already running for {email}")
    
    def show_error(self, message: str, suggestion: Optional[str] = None):
        """Show clean error message with helpful suggestion."""
        if suggestion:
            self.console.print(f"❌ {message} - {suggestion}")
        else:
            self.console.print(f"❌ {message}")
    
    def show_status(self, installed: bool, running: bool, email: Optional[str] = None, data_dir: Optional[str] = None):
        """Show clean status summary."""
        if not installed:
            self.console.print("📦 SyftBox not installed")
        elif not running:
            self.console.print("⏸️ SyftBox installed but not running")
        else:
            self.console.print(f"✅ SyftBox running for {email}" if email else "✅ SyftBox running")
    
    def show_uninstall_warning(self) -> bool:
        """Show uninstall warning and get confirmation."""
        response = self.console.input("⚠️ Remove SyftBox and all data? Type 'yes' to confirm: ")
        return response.lower() == 'yes'
    
    def show_uninstall_progress(self):
        """Show clean uninstall progress."""
        self.console.print("✅ SyftBox removed successfully")


# Global display instance
display = SyftDisplay()