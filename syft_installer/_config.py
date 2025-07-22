import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from syft_installer._utils import ConfigError, RuntimeEnvironment


@dataclass
class Config:
    """SyftBox configuration."""
    email: str
    data_dir: Optional[str] = None
    server_url: str = "https://syftbox.net"
    client_url: str = "http://localhost:7938"
    refresh_token: Optional[str] = None
    
    def __post_init__(self):
        """Set default data_dir if not provided."""
        if not self.data_dir:
            self.data_dir = RuntimeEnvironment().default_data_dir
    
    def to_dict(self) -> dict:
        """Convert config to dictionary (replacement for model_dump)."""
        from dataclasses import asdict
        return asdict(self)
    
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
            
            # Ensure data_dir is set
            if "data_dir" not in data or not data["data_dir"]:
                data["data_dir"] = RuntimeEnvironment().default_data_dir
                
            return cls(**data)
        except Exception as e:
            # Return None instead of raising an exception
            # This could happen if the file is corrupted or has wrong format
            return None
    
def load_config() -> Optional[Config]:
    """Load existing configuration."""
    return Config.load()


