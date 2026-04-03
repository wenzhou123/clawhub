#!/usr/bin/env python3
"""
ClawHub CLI 主程序
"""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from . import __version__
from .auth import login, logout, get_current_user
from .images import pull_image, push_image, list_images, delete_image
from .repos import list_repos, create_repo, delete_repo

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="clawhub")
@click.option(
    "--config",
    "-c",
    type=click.Path(),
    help="配置文件路径",
)
@click.option(
    "--registry",
    "-r",
    default="https://clawhub.io",
    help="Registry 地址",
    envvar="CLAWHUB_REGISTRY",
)
@click.pass_context
def cli(ctx: click.Context, config: str, registry: str) -> None:
    """ClawHub CLI - 容器镜像仓库管理工具"""
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config or Path.home() / ".clawhub" / "config.toml"
    ctx.obj["registry"] = registry


@cli.command()
@click.option("--username", "-u", prompt=True, help="用户名")
@click.option("--password", "-p", prompt=True, hide_input=True, help="密码")
@click.pass_context
def auth_login(ctx: click.Context, username: str, password: str) -> None:
    """登录到 ClawHub"""
    try:
        login(ctx.obj["registry"], username, password)
        console.print(f"[green]成功登录为 {username}[/green]")
    except Exception as e:
        console.print(f"[red]登录失败: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.pass_context
def auth_logout(ctx: click.Context) -> None:
    """登出 ClawHub"""
    logout()
    console.print("[green]已登出[/green]")


@cli.command(name="whoami")
def whoami() -> None:
    """显示当前登录用户"""
    user = get_current_user()
    if user:
        console.print(f"[green]当前用户: {user['username']} ({user['email']})[/green]")
    else:
        console.print("[yellow]未登录[/yellow]")


@cli.command()
@click.argument("image")
@click.option("--tag", "-t", default="latest", help="镜像标签")
@click.pass_context
def pull(ctx: click.Context, image: str, tag: str) -> None:
    """拉取镜像"""
    try:
        with console.status(f"[bold green]正在拉取 {image}:{tag}..."):
            pull_image(ctx.obj["registry"], image, tag)
        console.print(f"[green]成功拉取 {image}:{tag}[/green]")
    except Exception as e:
        console.print(f"[red]拉取失败: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("image")
@click.option("--tag", "-t", default="latest", help="镜像标签")
@click.option("--public", is_flag=True, help="设为公开镜像")
@click.pass_context
def push(ctx: click.Context, image: str, tag: str, public: bool) -> None:
    """推送镜像"""
    try:
        with console.status(f"[bold green]正在推送 {image}:{tag}..."):
            push_image(ctx.obj["registry"], image, tag, public=public)
        console.print(f"[green]成功推送 {image}:{tag}[/green]")
    except Exception as e:
        console.print(f"[red]推送失败: {e}[/red]")
        sys.exit(1)


@cli.command(name="images")
@click.option("--repo", "-r", help="仓库名称")
@click.option("--limit", "-l", default=20, help="返回数量限制")
@click.pass_context
def list_images_cmd(ctx: click.Context, repo: str, limit: int) -> None:
    """列出镜像"""
    try:
        images = list_images(ctx.obj["registry"], repo=repo, limit=limit)
        
        table = Table(title="镜像列表")
        table.add_column("名称", style="cyan")
        table.add_column("标签", style="magenta")
        table.add_column("大小", style="green")
        table.add_column("更新时间", style="yellow")
        
        for img in images:
            table.add_row(
                img["name"],
                img["tag"],
                img["size"],
                img["updated_at"],
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]获取镜像列表失败: {e}[/red]")
        sys.exit(1)


@cli.command(name="repos")
@click.option("--org", "-o", help="组织名称")
@click.option("--limit", "-l", default=20, help="返回数量限制")
@click.pass_context
def list_repos_cmd(ctx: click.Context, org: str, limit: int) -> None:
    """列出仓库"""
    try:
        repos = list_repos(ctx.obj["registry"], org=org, limit=limit)
        
        table = Table(title="仓库列表")
        table.add_column("名称", style="cyan")
        table.add_column("描述", style="white")
        table.add_column("公开", style="magenta")
        table.add_column("拉取次数", style="green")
        
        for repo in repos:
            table.add_row(
                repo["name"],
                repo.get("description", "-"),
                "是" if repo.get("is_public") else "否",
                str(repo.get("pull_count", 0)),
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]获取仓库列表失败: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("name")
@click.option("--description", "-d", help="仓库描述")
@click.option("--public", is_flag=True, help="设为公开仓库")
@click.pass_context
def create_repo_cmd(ctx: click.Context, name: str, description: str, public: bool) -> None:
    """创建仓库"""
    try:
        create_repo(ctx.obj["registry"], name, description=description, is_public=public)
        console.print(f"[green]成功创建仓库: {name}[/green]")
    except Exception as e:
        console.print(f"[red]创建仓库失败: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("name")
@click.confirmation_option(prompt="确定要删除这个镜像吗?")
@click.pass_context
def delete(ctx: click.Context, name: str) -> None:
    """删除镜像"""
    try:
        delete_image(ctx.obj["registry"], name)
        console.print(f"[green]成功删除镜像: {name}[/green]")
    except Exception as e:
        console.print(f"[red]删除失败: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """检查 ClawHub 服务状态"""
    import httpx
    
    try:
        response = httpx.get(f"{ctx.obj['registry']}/health", timeout=5)
        if response.status_code == 200:
            console.print("[green]✓ ClawHub 服务运行正常[/green]")
        else:
            console.print(f"[yellow]⚠ 服务状态异常: {response.status_code}[/yellow]")
    except httpx.ConnectError:
        console.print(f"[red]✗ 无法连接到 {ctx.obj['registry']}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    cli()
