"""Login command."""

import click
from getpass import getpass
from rich.console import Console
from rich.panel import Panel

from claw.api import get_api, APIError
from claw.config import config_manager

console = Console()


@click.command()
@click.option("--username", "-u", help="Username")
@click.option("--password", "-p", help="Password (not recommended, use interactive prompt)")
@click.option("--server", "-s", help="Server URL")
def login(username: str, password: str, server: str):
    """Login to ClawHub."""
    # Check if already logged in
    config = config_manager.load()
    if config.is_logged_in:
        console.print("[yellow]Already logged in. Use 'claw logout' first if you want to switch accounts.[/yellow]")
        return
    
    # Get username
    if not username:
        username = click.prompt("Username")
    
    # Get password securely
    if not password:
        password = getpass("Password: ")
    
    # Update server URL if provided
    if server:
        config_manager.set_api_url(server)
    
    # Attempt login
    try:
        api = get_api()
        result = api.login(username, password)
        
        token = result.get("token") or result.get("access_token")
        if not token:
            console.print("[red]Error: No token received from server[/red]")
            return
        
        # Save token
        config_manager.set_token(token)
        
        # Display success
        user_info = result.get("user", {})
        name = user_info.get("name") or user_info.get("username") or username
        
        console.print(Panel.fit(
            f"[green]Welcome, {name}![/green]\n"
            f"Successfully logged into ClawHub.",
            title="Login Successful",
            border_style="green"
        ))
        
    except APIError as e:
        console.print(f"[red]Login failed:[/red] {e.message}")
        if e.status_code == 401:
            console.print("[dim]Tip: Check your username and password[/dim]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
