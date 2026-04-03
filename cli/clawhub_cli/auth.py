"""
认证相关功能
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any

import httpx


def get_config_dir() -> Path:
    """获取配置目录"""
    config_dir = Path.home() / ".clawhub"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def get_credentials_path() -> Path:
    """获取凭证文件路径"""
    return get_config_dir() / "credentials.json"


def save_credentials(token: str, user: Dict[str, Any]) -> None:
    """保存凭证"""
    credentials = {
        "token": token,
        "user": user,
    }
    credentials_path = get_credentials_path()
    with open(credentials_path, "w") as f:
        json.dump(credentials, f)
    # 设置文件权限为仅用户可读
    credentials_path.chmod(0o600)


def load_credentials() -> Optional[Dict[str, Any]]:
    """加载凭证"""
    credentials_path = get_credentials_path()
    if not credentials_path.exists():
        return None
    with open(credentials_path, "r") as f:
        return json.load(f)


def clear_credentials() -> None:
    """清除凭证"""
    credentials_path = get_credentials_path()
    if credentials_path.exists():
        credentials_path.unlink()


def login(registry: str, username: str, password: str) -> None:
    """登录并获取 token"""
    response = httpx.post(
        f"{registry}/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    response.raise_for_status()
    data = response.json()
    save_credentials(data["access_token"], data["user"])


def logout() -> None:
    """登出"""
    clear_credentials()


def get_current_user() -> Optional[Dict[str, Any]]:
    """获取当前登录用户"""
    credentials = load_credentials()
    if credentials:
        return credentials.get("user")
    return None


def get_auth_token() -> Optional[str]:
    """获取认证 token"""
    credentials = load_credentials()
    if credentials:
        return credentials.get("token")
    return None


def get_auth_headers() -> Dict[str, str]:
    """获取认证头"""
    token = get_auth_token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}
