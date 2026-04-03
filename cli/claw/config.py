"""Configuration management for Claw CLI."""

import os
import yaml
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class ServerConfig(BaseModel):
    """Server configuration."""
    url: str = Field(default="https://api.clawhub.io", description="ClawHub API URL")


class AuthConfig(BaseModel):
    """Authentication configuration."""
    token: Optional[str] = Field(default=None, description="JWT authentication token")


class Config(BaseModel):
    """Main configuration model."""
    server: ServerConfig = Field(default_factory=ServerConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)

    @property
    def is_logged_in(self) -> bool:
        """Check if user is logged in."""
        return self.auth.token is not None and len(self.auth.token) > 0


class ConfigManager:
    """Manages configuration file operations."""
    
    CONFIG_DIR = Path.home() / ".clawhub"
    CONFIG_FILE = CONFIG_DIR / "config.yaml"
    
    def __init__(self):
        self._config: Optional[Config] = None
    
    def ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> Config:
        """Load configuration from file."""
        if self._config is not None:
            return self._config
        
        if not self.CONFIG_FILE.exists():
            self._config = Config()
            return self._config
        
        try:
            with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            self._config = Config(**data)
        except Exception as e:
            # If loading fails, return default config
            self._config = Config()
        
        return self._config
    
    def save(self, config: Config) -> None:
        """Save configuration to file."""
        self.ensure_config_dir()
        self._config = config
        
        with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
            yaml.dump(
                config.model_dump(),
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )
    
    def get_token(self) -> Optional[str]:
        """Get current authentication token."""
        return self.load().auth.token
    
    def set_token(self, token: str) -> None:
        """Set authentication token."""
        config = self.load()
        config.auth.token = token
        self.save(config)
    
    def clear_token(self) -> None:
        """Clear authentication token (logout)."""
        config = self.load()
        config.auth.token = None
        self.save(config)
    
    def get_api_url(self) -> str:
        """Get API base URL."""
        return self.load().server.url
    
    def set_api_url(self, url: str) -> None:
        """Set API base URL."""
        config = self.load()
        config.server.url = url.rstrip("/")
        self.save(config)


# Global config manager instance
config_manager = ConfigManager()
