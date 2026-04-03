"""List command."""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from claw.api import get_api, APIError
from claw.config import config_manager

console = Console()


@click.command(name="list")
@click.option("--namespace", "-n", help="Filter by namespace")
@click.option("--all", "-a", "show_all", is_flag=True, help="Show all accessible lobsters")
def list_cmd(namespace: str, show_all: bool):
    """List Lobsters.
    
    By default, lists your lobsters. Use --all to see public lobsters.
    """
    config = config_manager.load()
    
    try:
        api = get_api()
        
        if show_all:
            # Search for all public lobsters
            results = api.search_lobsters("*", limit=100)
            title = "Public Lobsters"
        else:
            if not config.is_logged_in:
                console.print("[red]Not logged in. Use 'claw login' first, or use --all to see public lobsters.[/red]")
                return
            
            results = api.list_my_lobsters()
            title = "My Lobsters"
        
        if not results:
            console.print(f"[yellow]No lobsters found.[/yellow]")
            if not show_all:
                console.print("[dim]Use 'claw push' to publish your first lobster![/dim]")
            return
        
        # Create results table
        table = Table(title=title)
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Latest", style="dim", justify="center")
        table.add_column("Visibility", style="yellow", justify="center")
        table.add_column("Downloads", style="green", justify="right")
        
        for item in results:
            name = f"{item.get('namespace', 'unknown')}/{item.get('name', 'unknown')}"
            description = item.get("description", "")[:40]
            if len(item.get("description", "")) > 40:
                description += "..."
            version = item.get("latest_version", "-")
            visibility = "public" if item.get("is_public", True) else "private"
            downloads = str(item.get("downloads", 0))
            
            table.add_row(name, description, version, visibility, downloads)
        
        console.print(table)
        console.print(f"\n[dim]Total: {len(results)} lobster(s)[/dim]")
        
    except APIError as e:
        if e.status_code == 401:
            console.print("[red]Session expired. Please login again.[/red]")
        else:
            console.print(f"[red]Failed to list lobsters:[/red] {e.message}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
