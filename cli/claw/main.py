#!/usr/bin/env python3
"""ClawHub CLI - Main entry point."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from claw import __version__
from claw.commands.login import login
from claw.commands.logout import logout
from claw.commands.whoami import whoami
from claw.commands.push import push
from claw.commands.pull import pull
from claw.commands.search import search
from claw.commands.list_cmd import list_cmd
from claw.commands.init import init

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="claw")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx: click.Context, verbose: bool):
    """ClawHub CLI - Manage OpenClaw Lobsters.
    
    ClawHub is a platform for sharing OpenClaw Agent configurations (Lobsters).
    
    Common commands:
        claw login          Authenticate with ClawHub
        claw init <name>    Create a new lobster
        claw push <path>    Publish a lobster
        claw pull <ref>     Download a lobster
        claw search <term>  Find lobsters
    
    For more help: https://docs.clawhub.io
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


# Register commands
cli.add_command(login)
cli.add_command(logout)
cli.add_command(whoami)
cli.add_command(push)
cli.add_command(pull)
cli.add_command(search)
cli.add_command(list_cmd)
cli.add_command(init)


@cli.command()
def docs():
    """Open ClawHub documentation."""
    import webbrowser
    webbrowser.open("https://docs.clawhub.io")


@cli.command()
@click.argument("topic", required=False)
def help(topic: str):
    """Show help for a specific topic."""
    if topic == "lobster":
        console.print(Panel.fit(
            "[bold]What is a Lobster?[/bold]\n\n"
            "A Lobster is a packaged OpenClaw Agent configuration.\n\n"
            "Each lobster contains:\n"
            "  [cyan]SOUL.md[/cyan]     - Personality and behavior definition\n"
            "  [cyan]AGENTS.md[/cyan]   - Technical configuration and tools\n"
            "  [cyan]IDENTITY.md[/cyan] - Metadata and branding\n\n"
            "Lobsters can be shared on ClawHub and installed by others.",
            title="Help: Lobster",
            border_style="blue"
        ))
    elif topic == "pack":
        console.print(Panel.fit(
            "[bold].clawpack Format[/bold]\n\n"
            "A .clawpack file is a tar.gz archive containing:\n"
            "  - manifest.json (metadata)\n"
            "  - SOUL.md\n"
            "  - AGENTS.md\n"
            "  - IDENTITY.md\n"
            "  - Additional files (README, LICENSE, etc.)\n\n"
            "Create with: [cyan]claw push <directory>[/cyan]\n"
            "Extract with: [cyan]claw pull <reference>[/cyan]",
            title="Help: Pack",
            border_style="blue"
        ))
    else:
        # Show general help
        click.echo(cli.get_help(click.Context(cli)))


if __name__ == "__main__":
    cli()
