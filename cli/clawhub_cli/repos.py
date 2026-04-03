"""
仓库管理相关功能
"""

from typing import List, Optional, Dict, Any

import httpx

from .auth import get_auth_headers


def list_repos(
    registry: str,
    org: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """列出仓库"""
    headers = get_auth_headers()
    params = {"limit": limit}
    if org:
        params["organization"] = org
    
    response = httpx.get(
        f"{registry}/api/v1/repositories",
        headers=headers,
        params=params,
    )
    response.raise_for_status()
    return response.json()["items"]


def create_repo(
    registry: str,
    name: str,
    description: Optional[str] = None,
    is_public: bool = False,
) -> Dict[str, Any]:
    """创建仓库"""
    headers = get_auth_headers()
    if not headers:
        raise RuntimeError("请先登录: clawhub login")
    
    data = {
        "name": name,
        "is_public": is_public,
    }
    if description:
        data["description"] = description
    
    response = httpx.post(
        f"{registry}/api/v1/repositories",
        headers=headers,
        json=data,
    )
    response.raise_for_status()
    return response.json()


def delete_repo(registry: str, name: str) -> None:
    """删除仓库"""
    headers = get_auth_headers()
    if not headers:
        raise RuntimeError("请先登录: clawhub login")
    
    response = httpx.delete(
        f"{registry}/api/v1/repositories/{name}",
        headers=headers,
    )
    response.raise_for_status()


def get_repo(registry: str, name: str) -> Dict[str, Any]:
    """获取仓库详情"""
    headers = get_auth_headers()
    
    response = httpx.get(
        f"{registry}/api/v1/repositories/{name}",
        headers=headers,
    )
    response.raise_for_status()
    return response.json()
