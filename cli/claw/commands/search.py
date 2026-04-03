"""Search command."""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from claw.api import get_api, APIError

console = Console()


@click.command()
@click.argument("keyword")
@click.option("--limit", "-l", default=20, help="Maximum number of results")
@click.option("--sort", "-s", type=click.Choice(["relevance", "downloads", "updated"]), 
              default="relevance", help="Sort results")
def search(keyword: str, limit: int, sort: str):
    """Search for Lobsters on ClawHub.
    
    KEYWORD is the search term to look for.
    """
    try:
        api = get_api()
        results = api.search_lobsters(keyword, limit=limit)
        
        if not results:
            console.print(f"[yellow]No results found for '{keyword}'[/yellow]")
            return
        
        # Create results table
        table = Table(title=f"Search Results for '{keyword}'")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Version", style="dim", justify="center")
        table.add_column("Downloads", style="green", justify="right")
        table.add_column("Updated", style="dim")
        
        for item in results:
            name = f"{item.get('namespace', 'unknown')}/{item.get('name', 'unknown')}"
            description = item.get("description", "")[:50]
            if len(item.get("description", "")) > 50:
                description += "..."
            version = item.get("latest_version", "-")
            downloads = str(item.get("downloads", 0))
            updated = item.get("updated_at", "-")
            if updated != "-":
                # Format date
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                    updated = dt.strftime("%Y-%m-%d")
                except:
                    pass
            
            table.add_row(name, description, version, downloads, updated)
        
        console.print(table)
        console.print(f"\n[dim]Found {len(results)} result(s)[/dim]")
        
    except APIError as e:
        console.print(f"[red]Search failed:[/red] {e.message}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
