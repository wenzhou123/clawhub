"""Pull command."""

import os
import re
import tempfile
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, DownloadColumn, TransferSpeedColumn

from claw.api import get_api, APIError
from claw.config import config_manager
from claw.packager import unpack, PackageError

console = Console()

# Regex to parse lobster reference: namespace/name:version
LOBSTER_REF_PATTERN = re.compile(r"^(?:(?P<namespace>[^/]+)/)?(?P<name>[^:@]+)(?::(?P<version>[^/]+))?$")


def parse_lobster_ref(ref: str) -> tuple[str, str, str]:
    """Parse lobster reference string.
    
    Format: [namespace/]name[:version]
    Default: namespace=user's namespace, version=latest
    
    Returns:
        Tuple of (namespace, name, version)
    """
    match = LOBSTER_REF_PATTERN.match(ref)
    if not match:
        raise ValueError(f"Invalid lobster reference: {ref}")
    
    namespace = match.group("namespace")
    name = match.group("name")
    version = match.group("version") or "latest"
    
    if not namespace:
        # Try to use user's namespace
        try:
            config = config_manager.load()
            if config.is_logged_in:
                api = get_api()
                user = api.get_current_user()
                namespace = user.get("namespace") or user.get("username")
        except:
            pass
        
        if not namespace:
            raise ValueError(f"No namespace specified and not logged in")
    
    return namespace, name, version


@click.command()
@click.argument("reference")
@click.option("--output", "-o", help="Output directory (default: ./<name>-<version>)")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing directory")
def pull(reference: str, output: str, force: bool):
    """Download a Lobster from ClawHub.
    
    REFERENCE format: [namespace/]name[:version]
    
    Examples:
        claw pull myagent           # Pull from your namespace, latest version
        claw pull john/myagent:1.0  # Pull specific version
        claw pull myagent:2.0       # Pull from your namespace, version 2.0
    """
    # Parse reference
    try:
        namespace, name, version = parse_lobster_ref(reference)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        console.print("[dim]Usage: claw pull [namespace/]name[:version][/dim]")
        return
    
    # Determine output directory
    if output:
        output_dir = Path(output).resolve()
    else:
        output_dir = Path.cwd() / f"{name}-{version}"
    
    if output_dir.exists() and not force:
        console.print(f"[red]Error:[/red] Directory already exists: {output_dir}")
        console.print("[dim]Use -f/--force to overwrite[/dim]")
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        DownloadColumn(),
        TransferSpeedColumn(),
        console=console,
    ) as progress:
        download_task = progress.add_task(
            f"[cyan]Downloading {namespace}/{name}:{version}...",
            total=None,
        )
        
        try:
            # Create temp file for download
            with tempfile.NamedTemporaryFile(suffix=".clawpack", delete=False) as tmp:
                tmp_path = tmp.name
            
            api = get_api()
            api.download_lobster(
                namespace=namespace,
                name=name,
                version=version,
                output_path=tmp_path,
            )
            
            progress.update(download_task, completed=True)
            
            # Unpack
            unpack_task = progress.add_task("[cyan]Extracting...", total=None)
            extract_dir, manifest = unpack(Path(tmp_path), output_dir.parent)
            
            # Rename to desired output name if needed
            if output_dir != extract_dir:
                if output_dir.exists():
                    import shutil
                    shutil.rmtree(output_dir)
                extract_dir.rename(output_dir)
            
            progress.update(unpack_task, completed=True)
            
            # Clean up temp file
            os.unlink(tmp_path)
            
            # Show success
            console.print(Panel.fit(
                f"[green]Successfully pulled {namespace}/{name}:{version}[/green]\n\n"
                f"Name: [cyan]{manifest.name}[/cyan]\n"
                f"Version: [cyan]{manifest.version}[/cyan]\n"
                f"Author: [cyan]{manifest.author or 'Unknown'}[/cyan]\n"
                f"Files: [cyan]{len(manifest.files)}[/cyan]\n\n"
                f"Extracted to: [cyan]{output_dir}[/cyan]",
                title="Pull Complete",
                border_style="green"
            ))
            
        except APIError as e:
            progress.update(download_task, completed=True)
            if e.status_code == 404:
                console.print(f"[red]Not found:[/red] {namespace}/{name}:{version}")
            else:
                console.print(f"[red]Download failed:[/red] {e.message}")
            # Clean up temp file
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.unlink(tmp_path)
        except PackageError as e:
            progress.update(download_task, completed=True)
            console.print(f"[red]Extraction failed:[/red] {e}")
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.unlink(tmp_path)
        except Exception as e:
            progress.update(download_task, completed=True)
            console.print(f"[red]Error:[/red] {e}")
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.unlink(tmp_path)
