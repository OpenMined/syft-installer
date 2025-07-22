"""
Single-line progress system with rich technical details.

Shows engaging technical progress on a single line using carriage returns,
never breaking to new lines but showing all the juicy installation details.
"""
import time
import sys
from typing import Optional


class SingleLineProgress:
    """Single-line progress bar with scrolling technical details."""
    
    def __init__(self):
        self.current_step = 0
        self.total_steps = 100
        self.current_message = ""
        self.is_active = False
    
    def start(self, total_steps: int = 100):
        """Start the progress display."""
        self.total_steps = total_steps
        self.current_step = 0
        self.is_active = True
        self._update_display()
    
    def update(self, step: int, message: str):
        """Update progress with new step and message."""
        if not self.is_active:
            return
            
        self.current_step = min(step, self.total_steps)
        self.current_message = message
        self._update_display()
    
    def finish(self, final_message: str):
        """Finish progress and show final clean message."""
        if not self.is_active:
            return
            
        # Clear the line completely
        sys.stdout.write('\r' + ' ' * 120 + '\r')
        sys.stdout.flush()
        
        # Show final clean message
        print(final_message)
        self.is_active = False
    
    def _update_display(self):
        """Update the single-line display with progress bar and message."""
        if not self.is_active:
            return
        
        # Calculate progress percentage
        percentage = int((self.current_step / self.total_steps) * 100)
        
        # Create progress bar (20 characters)
        filled = int((self.current_step / self.total_steps) * 20)
        bar = '█' * filled + '░' * (20 - filled)
        
        # Truncate message to fit terminal width (assume 120 chars max)
        max_message_len = 80
        display_message = self.current_message
        if len(display_message) > max_message_len:
            display_message = display_message[:max_message_len-3] + "..."
        
        # Build the display line
        display_line = f"🚀 [{bar}] {percentage:3d}% {display_message}"
        
        # Write with carriage return (no newline)
        sys.stdout.write(f'\r{display_line}')
        sys.stdout.flush()


# Global progress instance
progress = SingleLineProgress()


def show_progress(step: int, message: str, total: int = 100):
    """Show progress update on single line."""
    if not progress.is_active:
        progress.start(total)
    progress.update(step, message)


def finish_progress(final_message: str):
    """Finish progress and show clean final message."""
    progress.finish(final_message)


def progress_context():
    """Context manager for progress display."""
    class ProgressContext:
        def __init__(self):
            self.started = False
        
        def update(self, step: int, message: str, total: int = 100):
            if not self.started:
                progress.start(total)
                self.started = True
            progress.update(step, message)
        
        def finish(self, final_message: str):
            if self.started:
                progress.finish(final_message)
    
    return ProgressContext()