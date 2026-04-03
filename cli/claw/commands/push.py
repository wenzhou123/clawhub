"""Push command."""

import os
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from claw.api import get_api, APIError
from claw.config import config_manager
from claw.packager import pack, PackageError, validate_lobster_directory

console = Console()


@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--namespace", "-n", help="Namespace (username or organization)")
@click.option("--name", help="Lobster name (default: directory name)")
@click.option("--version", "-v", default="0.1.0", help="Version (semver)")
@click.option("--description", "-d", help="Short description")
@click.option("--tag", "tags", multiple=True, help="Tags (can be used multiple times)")
@click.option("--public", is_flag=True, help="Make the lobster public")
@click.option("--force", "-f", is_flag=True, help="Force push even if validation warns")
def push(path: str, namespace: str, name: str, version: str, description: str, tags: tuple, public: bool, force: bool):
    """Pack and upload a Lobster to ClawHub.
    
    PATH is the directory containing the lobster files.
    """
    config = config_manager.load()
    
    if not config.is_logged_in:
        console.print("[red]Not logged in. Use 'claw login' first.[/red]")
        return
    
    source_path = Path(path).resolve()
    
    if not source_path.is_dir():
        console.print(f"[red]Error:[/red] {path} is not a directory")
        return
    
    # Validate directory
    is_valid, missing = validate_lobster_directory(source_path)
    if not is_valid:
        console.print(f"[red]Validation failed - missing required files:[/red]")
        for f in missing:
            console.print(f"  - [red]{f}[/red]")
        if not force:
            return
        console.print("[yellow]Continuing anyway due to --force flag...[/yellow]")
    
    # Get namespace
    if not namespace:
        try:
            api = get_api()
            user = api.get_current_user()
            namespace = user.get("namespace") or user.get("username")
        except APIError as e:
            console.print(f"[red]Failed to get user namespace:[/red] {e.message}")
            return
    
    pkg_name = name or source_path.name
    
    # Get description from IDENTITY.md if not provided
    if not description:
        identity_file = source_path / "IDENTITY.md"
        if identity_file.exists():
            content = identity_file.read_text(encoding="utf-8")
            for line in content.split("\n"):
                if line.startswith("## Description"):
                    desc = content.split("## Description")[1].split("##")[0].strip()
                    description = desc.split("\n")[0].strip()
                    break
    
    # Get author from git config or user info
    author = ""
    try:
        api = get_api()
        user = api.get_current_user()
        author = user.get("name") or user.get("username", "")
    except:
        pass
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Pack the lobster
        pack_task = progress.add_task(f"[cyan]Packing {pkg_name}...", total=None)
        
        try:
            package_path = pack(
                source_path=source_path,
                namespace=namespace,
                name=pkg_name,
                version=version,
                description=description,
                author=author,
                tags=list(tags) if tags else None,
            )
            progress.update(pack_task, completed=True)
        except PackageError as e:
            progress.update(pack_task, completed=True)
            console.print(f"[red]Packaging failed:[/red] {e}")
            return
        
        # Upload
        upload_task = progress.add_task(f"[cyan]Uploading to ClawHub...", total=None)
        
        try:
            api = get_api()
            result = api.upload_lobster(
                namespace=namespace,
                name=pkg_name,
                version=version,
                file_path=str(package_path),
                description=description,
            )
            progress.update(upload_task, completed=True)
            
            # Clean up temporary package file
            package_path.unlink()
            
            # Show success
            visibility = "public" if public else "private"
            console.print(Panel.fit(
                f"[green]Successfully pushed {namespace}/{pkg_name}:{version}[/green]\n\n"
                f"Name: [cyan]{pkg_name}[/cyan]\n"
                f"Namespace: [cyan]{namespace}[/cyan]\n"
                f"Version: [cyan]{version}[/cyan]\n"
                f"Visibility: [cyan]{visibility}[/cyan]",
                title="Push Complete",
                border_style="green"
            ))
            
            console.print(f"\n[dim]View at: {config.server.url}/lobsters/{namespace}/{pkg_name}[/dim]")
            
        except APIError as e:
            progress.update(upload_task, completed=True)
            console.print(f"[red]Upload failed:[/red] {e.message}")
            if e.status_code == 409:
                console.print("[dim]Tip: This version already exists. Use a different version.[/dim]")
            elif e.status_code == 413:
                console.print("[dim]Tip: Package file is too large.[/dim]")
            # Clean up on failure
            if package_path.exists():
                package_path.unlink()
        except Exception as e:
            progress.update(upload_task, completed=True)
            console.print(f"[red]Error:[/red] {e}")
            if package_path.exists():
                package_path.unlink()
