"""Whoami command."""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from claw.api import get_api, APIError
from claw.config import config_manager

console = Console()


@click.command()
@click.option("--token", is_flag=True, help="Show authentication token")
def whoami(token: bool):
    """Display current user information."""
    config = config_manager.load()
    
    if not config.is_logged_in:
        console.print("[yellow]Not logged in. Use 'claw login' to authenticate.[/yellow]")
        return
    
    try:
        api = get_api()
        user = api.get_current_user()
        
        # Build info table
        table = Table(show_header=False, box=None)
        table.add_column("Key", style="cyan", justify="right")
        table.add_column("Value", style="white")
        
        table.add_row("Username:", user.get("username", "N/A"))
        table.add_row("Name:", user.get("name", "N/A"))
        table.add_row("Email:", user.get("email", "N/A"))
        table.add_row("Namespace:", user.get("namespace", user.get("username", "N/A")))
        
        if user.get("bio"):
            table.add_row("Bio:", user.get("bio"))
        
        table.add_row("Server:", config.server.url)
        
        if token:
            # Show masked token
            full_token = config.auth.token
            masked = full_token[:10] + "..." + full_token[-10:] if len(full_token) > 20 else "***"
            table.add_row("Token:", masked)
        
        console.print(Panel.fit(
            table,
            title="User Information",
            border_style="blue"
        ))
        
    except APIError as e:
        if e.status_code == 401:
            console.print("[red]Session expired or invalid. Please login again.[/red]")
            config_manager.clear_token()
        else:
            console.print(f"[red]Error:[/red] {e.message}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
