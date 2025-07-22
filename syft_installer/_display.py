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
        
        # Create progress bars for different phases
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console
        )
        
        # Create main installation task
        main_task = progress.add_task("🚀 Welcome to SyftBox!", total=100)
        
        class ProgressContext:
            def __init__(self, progress_obj, main_task_id):
                self.progress = progress_obj
                self.main_task = main_task_id
                
            def update_phase(self, description: str, percent: int):
                """Update the current phase with clean messaging."""
                self.progress.update(self.main_task, description=description, completed=percent)
            
            def show_downloading(self, total_bytes: int) -> int:
                """Show download progress and return task ID."""
                download_task = self.progress.add_task("📥 Downloading SyftBox", total=total_bytes)
                return download_task
            
            def update_download(self, task_id: int, completed: int):
                """Update download progress."""
                self.progress.update(task_id, completed=completed)
            
            def complete_download(self, task_id: int):
                """Complete download phase."""
                self.progress.update(task_id, completed=self.progress.tasks[task_id].total)
                self.progress.remove_task(task_id)
        
        with Live(progress, console=self.console, refresh_per_second=10) as live:
            self._current_progress = progress
            self._current_live = live
            yield ProgressContext(progress, main_task)
            self._current_progress = None
            self._current_live = None
    
    def show_welcome(self, version: str):
        """Show inspiring welcome message."""
        welcome_text = Text()
        welcome_text.append("🌟 ", style="yellow")
        welcome_text.append("Welcome to SyftBox", style="bold blue")
        welcome_text.append(" - where privacy meets collaboration", style="dim")
        
        panel = Panel(
            welcome_text,
            border_style="blue",
            padding=(0, 1)
        )
        self.console.print(panel)
        self.console.print()
    
    def show_email_detection(self, email: str, is_colab: bool = False):
        """Show clean email detection message."""
        if is_colab:
            self.console.print(f"✨ Auto-detected your Google account: [cyan]{email}[/cyan]")
        else:
            self.console.print(f"👋 Installing for: [cyan]{email}[/cyan]")
        self.console.print()
    
    def show_otp_request(self, email: str):
        """Show clean OTP request message."""
        self.console.print(f"📧 Verification code sent to [cyan]{email}[/cyan]")
        self.console.print("💡 [dim]Check your inbox (and spam folder)[/dim]")
        self.console.print()
    
    def get_otp_input(self) -> str:
        """Get OTP input with clean prompt."""
        return self.console.input("🔐 Enter your 8-digit verification code: ")
    
    def show_success(self, email: str, data_dir: str):
        """Show inspiring success message."""
        # Clear any remaining progress
        self.console.clear()
        
        success_text = Text()
        success_text.append("🎉 ", style="green")
        success_text.append("SyftBox is ready!", style="bold green")
        success_text.append(" Welcome to the privacy-preserving future.", style="dim")
        
        # Create info table
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
        table.add_column("", style="cyan", width=12)
        table.add_column("", style="white")
        
        table.add_row("📧 Email", email)
        table.add_row("📁 Data folder", data_dir)
        table.add_row("🌐 Status", "[green]Running[/green]")
        
        panel = Panel(
            Text.from_markup(f"{success_text}\n\n") + table,
            border_style="green",
            title="[bold green]Installation Complete[/bold green]",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
        self.console.print("💫 [dim]Ready to build something amazing? Check out the apps at[/dim] [link=https://syftbox.net]syftbox.net[/link]")
        self.console.print()
    
    def show_already_running(self, email: str):
        """Show message when SyftBox is already running."""
        self.console.print("✨ [green]SyftBox is already running![/green]")
        self.console.print(f"👋 [dim]Connected as[/dim] [cyan]{email}[/cyan]")
        self.console.print()
    
    def show_error(self, message: str, suggestion: Optional[str] = None):
        """Show clean error message with helpful suggestion."""
        error_text = Text()
        error_text.append("❌ ", style="red")
        error_text.append(message, style="red")
        
        if suggestion:
            error_text.append(f"\n💡 {suggestion}", style="dim")
        
        panel = Panel(
            error_text,
            border_style="red",
            title="[bold red]Installation Issue[/bold red]",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_status(self, installed: bool, running: bool, email: Optional[str] = None, data_dir: Optional[str] = None):
        """Show clean status summary."""
        if not installed:
            self.console.print("📦 [yellow]SyftBox not installed[/yellow]")
            self.console.print("💡 [dim]Run[/dim] [cyan]si.install()[/cyan] [dim]to get started[/dim]")
            return
        
        if not running:
            self.console.print("⏸️  [yellow]SyftBox installed but not running[/yellow]")
            self.console.print("💡 [dim]Run[/dim] [cyan]si.run()[/cyan] [dim]to start[/dim]")
            return
        
        # Running successfully
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
        table.add_column("", style="cyan", width=12)
        table.add_column("", style="white")
        
        if email:
            table.add_row("📧 Email", email)
        if data_dir:
            table.add_row("📁 Data folder", data_dir)
        table.add_row("🌐 Status", "[green]Running[/green]")
        
        panel = Panel(
            table,
            border_style="green",
            title="[bold green]SyftBox Status[/bold green]",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_uninstall_warning(self) -> bool:
        """Show uninstall warning and get confirmation."""
        warning_text = Text()
        warning_text.append("⚠️  ", style="yellow")
        warning_text.append("This will permanently remove SyftBox and all your data.", style="yellow")
        
        panel = Panel(
            warning_text,
            border_style="yellow",
            title="[bold yellow]Uninstall Warning[/bold yellow]",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        response = self.console.input("\n💭 Type 'yes' to confirm removal: ")
        return response.lower() == 'yes'
    
    def show_uninstall_progress(self):
        """Show clean uninstall progress."""
        with self.console.status("[yellow]Removing SyftBox...[/yellow]", spinner="dots"):
            time.sleep(1)  # Give time for the removal to happen
        
        self.console.print("✅ [green]SyftBox removed successfully[/green]")
        self.console.print("👋 [dim]Thanks for trying SyftBox! We hope to see you again soon.[/dim]")
        self.console.print()


# Global display instance
display = SyftDisplay()