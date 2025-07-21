import json
import os
from pathlib import Path
from typing import Dict, Optional

from pydantic import BaseModel, Field

from syft_installer.exceptions import ConfigError
from syft_installer.runtime import RuntimeEnvironment


class Config(BaseModel):
    """SyftBox configuration."""
    email: str
    data_dir: str = Field(default_factory=lambda: RuntimeEnvironment().default_data_dir)
    server_url: str = "https://syftbox.net"
    client_url: str = "http://localhost:7938"
    refresh_token: Optional[str] = None
    
    @property
    def config_dir(self) -> Path:
        """Get configuration directory path."""
        return Path.home() / ".syftbox"
    
    @property
    def config_file(self) -> Path:
        """Get configuration file path."""
        return self.config_dir / "config.json"
    
    @property
    def binary_path(self) -> Path:
        """Get binary installation path."""
        return Path.home() / ".local" / "bin" / "syftbox"
    
    def save(self) -> None:
        """Save configuration to disk."""
        try:
            # Create config directory if it doesn't exist
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Don't save access token (only refresh token)
            # Use the exact field names expected by syftbox
            data = {
                "email": self.email,
                "data_dir": self.data_dir,
                "server_url": self.server_url,
                "client_url": self.client_url,
                "refresh_token": self.refresh_token
            }
            
            with open(self.config_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            raise ConfigError(f"Failed to save configuration: {str(e)}")
    
    @classmethod
    def load(cls) -> Optional["Config"]:
        """Load configuration from disk."""
        config_file = Path.home() / ".syftbox" / "config.json"
        
        if not config_file.exists():
            return None
        
        try:
            with open(config_file, "r") as f:
                data = json.load(f)
            return cls(**data)
        except Exception as e:
            raise ConfigError(f"Failed to load configuration: {str(e)}")
    
    def is_valid(self) -> bool:
        """Check if configuration has valid credentials."""
        return bool(self.email and self.refresh_token)


def load_config() -> Optional[Config]:
    """Load existing configuration."""
    return Config.load()


def is_installed() -> bool:
    """Check if SyftBox is installed."""
    config = load_config()
    if not config:
        return False
    
    # Check if binary exists
    if not config.binary_path.exists():
        return False
    
    # Check if config is valid
    return config.is_valid()


def get_config_dir() -> Path:
    """Get configuration directory path."""
    return Path.home() / ".syftbox"


def get_data_dir(config: Optional[Config] = None) -> Path:
    """Get data directory path."""
    if config:
        return Path(config.data_dir).expanduser()
    
    # Use runtime default
    return Path(RuntimeEnvironment().default_data_dir).expanduser()