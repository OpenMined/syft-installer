import sys
from typing import Optional, Union

from rich.console import Console
from rich.prompt import Prompt, Confirm

from syft_installer.exceptions import HeadlessError
from syft_installer.runtime import RuntimeEnvironment


class InputHandler:
    """Handle user input across different environments."""
    
    def __init__(self, runtime: RuntimeEnvironment, headless: bool = False):
        self.runtime = runtime
        self.headless = headless
        self.console = Console()
    
    def get_input(self, prompt: str, default: Optional[str] = None) -> str:
        """Get text input from user."""
        if self.headless:
            raise HeadlessError(f"Input required in headless mode: {prompt}")
        
        if self.runtime.can_use_widgets:
            return self._widget_input(prompt, default)
        elif self.runtime.has_tty:
            return self._terminal_input(prompt, default)
        else:
            raise HeadlessError(f"No input method available: {prompt}")
    
    def get_bool(self, prompt: str, default: bool = True) -> bool:
        """Get yes/no input from user."""
        if self.headless:
            return default
        
        if self.runtime.can_use_widgets:
            return self._widget_bool(prompt, default)
        elif self.runtime.has_tty:
            return Confirm.ask(prompt, default=default)
        else:
            return default
    
    def _terminal_input(self, prompt: str, default: Optional[str] = None) -> str:
        """Get input using terminal."""
        if default:
            return Prompt.ask(prompt, default=default)
        else:
            return Prompt.ask(prompt)
    
    def _widget_input(self, prompt: str, default: Optional[str] = None) -> str:
        """Get input using ipywidgets."""
        try:
            import ipywidgets as widgets
            from IPython.display import display, clear_output
            
            # For OTP input, just use a simple text widget
            if "OTP" in prompt:
                print(prompt)
                # Return empty string to indicate we're waiting for programmatic input
                return ""
            
            # For other inputs, use the widget approach
            # Create widgets
            label = widgets.Label(value=prompt)
            text = widgets.Text(value=default or "", placeholder="Enter value")
            button = widgets.Button(description="Submit")
            output = widgets.Output()
            
            # Result container
            result = {"value": None}
            
            def on_submit(b):
                result["value"] = text.value
                output.clear_output()
                with output:
                    print("✓ Submitted")
            
            button.on_click(on_submit)
            text.on_submit(lambda x: on_submit(None))  # Submit on Enter
            
            # Display widgets
            display(widgets.VBox([label, text, button, output]))
            
            # Wait for input
            while result["value"] is None:
                import time
                time.sleep(0.1)
            
            return result["value"]
            
        except ImportError:
            # Fallback to regular input
            return input(prompt)
    
    def _widget_bool(self, prompt: str, default: bool) -> bool:
        """Get boolean input using ipywidgets."""
        try:
            import ipywidgets as widgets
            from IPython.display import display
            
            # Create widgets
            label = widgets.Label(value=prompt)
            checkbox = widgets.Checkbox(value=default, description="Yes")
            button = widgets.Button(description="Submit")
            output = widgets.Output()
            
            # Result container
            result = {"value": None}
            
            def on_submit(b):
                result["value"] = checkbox.value
                output.clear_output()
                with output:
                    print("✓ Submitted")
            
            button.on_click(on_submit)
            
            # Display widgets
            display(widgets.VBox([label, checkbox, button, output]))
            
            # Wait for input
            while result["value"] is None:
                import time
                time.sleep(0.1)
            
            return result["value"]
            
        except ImportError:
            # Fallback to yes/no input
            response = input(f"{prompt} [Y/n]: ").lower()
            return response != "n"


class ProgressHandler:
    """Handle progress display across different environments."""
    
    def __init__(self, runtime: RuntimeEnvironment, callback: Optional[callable] = None):
        self.runtime = runtime
        self.callback = callback
        self.console = Console()
        self.widget = None
    
    def update(self, message: str, percent: int) -> None:
        """Update progress display."""
        if self.callback:
            self.callback("progress", message, percent)
        
        if self.runtime.can_use_widgets:
            self._update_widget(message, percent)
        elif self.runtime.has_tty:
            self._update_terminal(message, percent)
        # Silent in headless mode unless callback provided
    
    def error(self, message: str) -> None:
        """Display error message."""
        if self.callback:
            self.callback("error", message, 0)
        
        if self.runtime.has_tty:
            self.console.print(f"[red]✗ {message}[/red]")
        elif self.runtime.can_use_widgets:
            self._show_widget_error(message)
    
    def info(self, message: str) -> None:
        """Display info message."""
        if self.callback:
            self.callback("info", message, 0)
        
        if self.runtime.has_tty:
            self.console.print(f"[blue]ℹ {message}[/blue]")
        elif self.runtime.can_use_widgets:
            self._show_widget_info(message)
    
    def _update_terminal(self, message: str, percent: int) -> None:
        """Update terminal progress."""
        if percent >= 100:
            self.console.print(f"[green]✓ {message}[/green]")
        else:
            self.console.print(f"[yellow]⟳ {message} ({percent}%)[/yellow]")
    
    def _update_widget(self, message: str, percent: int) -> None:
        """Update widget progress."""
        try:
            import ipywidgets as widgets
            from IPython.display import display
            
            if not self.widget:
                self.widget = widgets.IntProgress(
                    value=0,
                    min=0,
                    max=100,
                    description="Progress:",
                    bar_style="info",
                )
                self.label = widgets.Label(value=message)
                display(widgets.VBox([self.widget, self.label]))
            
            self.widget.value = percent
            self.label.value = message
            
            if percent >= 100:
                self.widget.bar_style = "success"
                
        except ImportError:
            pass
    
    def _show_widget_error(self, message: str) -> None:
        """Show error in widget."""
        try:
            import ipywidgets as widgets
            from IPython.display import display
            
            error_widget = widgets.HTML(
                value=f'<div style="color: red;">✗ {message}</div>'
            )
            display(error_widget)
        except ImportError:
            pass
    
    def _show_widget_info(self, message: str) -> None:
        """Show info in widget."""
        try:
            import ipywidgets as widgets
            from IPython.display import display
            
            info_widget = widgets.HTML(
                value=f'<div style="color: blue;">ℹ {message}</div>'
            )
            display(info_widget)
        except ImportError:
            pass