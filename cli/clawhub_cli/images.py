"""
镜像管理相关功能
"""

import subprocess
from typing import List, Optional, Dict, Any

import httpx

from .auth import get_auth_headers


def pull_image(registry: str, image: str, tag: str = "latest") -> None:
    """
    拉取镜像
    
    实际调用 docker pull 命令
    """
    full_image = f"{registry.replace('https://', '').replace('http://', '')}/{image}:{tag}"
    result = subprocess.run(
        ["docker", "pull", full_image],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)


def push_image(registry: str, image: str, tag: str = "latest", public: bool = False) -> None:
    """
    推送镜像
    
    1. 给本地镜像打标签
    2. 推送到 registry
    """
    headers = get_auth_headers()
    if not headers:
        raise RuntimeError("请先登录: clawhub login")
    
    # 先创建仓库记录
    repo_name = image.split("/")[0] if "/" in image else image
    httpx.post(
        f"{registry}/api/v1/repositories",
        headers=headers,
        json={"name": repo_name, "is_public": public},
    )
    
    # 打标签并推送
    full_image = f"{registry.replace('https://', '').replace('http://', '')}/{image}:{tag}"
    local_image = f"{image}:{tag}"
    
    # 打标签
    result = subprocess.run(
        ["docker", "tag", local_image, full_image],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"打标签失败: {result.stderr}")
    
    # 推送
    result = subprocess.run(
        ["docker", "push", full_image],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"推送失败: {result.stderr}")


def list_images(
    registry: str,
    repo: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """列出镜像"""
    headers = get_auth_headers()
    params = {"limit": limit}
    if repo:
        params["repository"] = repo
    
    response = httpx.get(
        f"{registry}/api/v1/images",
        headers=headers,
        params=params,
    )
    response.raise_for_status()
    return response.json()["items"]


def delete_image(registry: str, image: str, tag: Optional[str] = None) -> None:
    """删除镜像"""
    headers = get_auth_headers()
    if not headers:
        raise RuntimeError("请先登录: clawhub login")
    
    url = f"{registry}/api/v1/images/{image}"
    if tag:
        url = f"{url}/tags/{tag}"
    
    response = httpx.delete(url, headers=headers)
    response.raise_for_status()
