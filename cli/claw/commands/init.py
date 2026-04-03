"""Init command."""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree

from claw.packager import init_lobster, REQUIRED_FILES

console = Console()


@click.command()
@click.argument("name")
@click.option("--path", "-p", help="Directory to initialize (default: ./<name>)")
@click.option("--description", "-d", default="", help="Short description")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing files")
@click.option("--non-interactive", is_flag=True, help="Skip interactive prompts")
def init(name: str, path: str, description: str, force: bool, non_interactive: bool):
    """Initialize a new Lobster configuration in the current directory.
    
    NAME is the name of your lobster.
    
    This creates the required configuration files:
    - SOUL.md: Core personality and behavior
    - AGENTS.md: Technical configuration
    - IDENTITY.md: Metadata and branding
    - README.md: Documentation
    """
    # Determine target path
    if path:
        target_path = Path(path).resolve()
    else:
        target_path = Path.cwd() / name
    
    # Check if directory exists and has files
    if target_path.exists():
        existing_files = [f for f in REQUIRED_FILES if (target_path / f).exists()]
        if existing_files and not force:
            console.print(f"[yellow]Directory already exists with lobster files:[/yellow]")
            for f in existing_files:
                console.print(f"  - {f}")
            console.print("[dim]Use --force to overwrite existing files[/dim]")
            return
    
    # Interactive prompts if not non-interactive
    author = ""
    if not non_interactive:
        author = click.prompt("Author name (optional)", default="", show_default=False)
        if not description:
            description = click.prompt("Description (optional)", default="", show_default=False)
    
    try:
        created_files = init_lobster(
            path=target_path,
            name=name,
            description=description,
            author=author,
        )
        
        # Show created files as tree
        tree = Tree(f"[cyan]{target_path.name}/[/cyan]")
        for f in created_files:
            tree.add(f"[green]{f.name}[/green]")
        
        console.print(Panel.fit(
            f"[green]Successfully initialized '{name}'![/green]\n\n"
            f"{tree}\n\n"
            "Next steps:\n"
            f"  1. Edit the configuration files in [cyan]{target_path}[/cyan]\n"
            f"  2. Run [cyan]claw push {target_path}[/cyan] to publish",
            title="Initialization Complete",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
