"""Logout command."""

import click
from rich.console import Console
from rich.panel import Panel

from claw.config import config_manager

console = Console()


@click.command()
def logout():
    """Logout from ClawHub."""
    config = config_manager.load()
    
    if not config.is_logged_in:
        console.print("[yellow]Not logged in.[/yellow]")
        return
    
    # Clear token
    config_manager.clear_token()
    
    console.print(Panel.fit(
        "[green]Successfully logged out.[/green]",
        title="Logout",
        border_style="green"
    ))
