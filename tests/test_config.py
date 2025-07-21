"""Unit tests for configuration module."""
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, Mock

from syft_installer.config import Config


class TestConfig:
    """Test Config class."""
    
    def test_init(self):
        """Test config initialization."""
        config = Config(
            email="test@example.com",
            server_url="https://syftbox.net",
            data_dir="/path/to/data",
            refresh_token="test_token"
        )
        
        assert config.email == "test@example.com"
        assert config.server_url == "https://syftbox.net"
        assert config.data_dir == "/path/to/data"
        assert config.refresh_token == "test_token"
        assert config.access_token is None
    
    def test_config_dir(self):
        """Test config directory path."""
        config = Config(
            email="test@example.com",
            server_url="https://syftbox.net",
            data_dir="/path/to/data"
        )
        
        expected = Path.home() / ".syftbox"
        assert config.config_dir == expected
    
    def test_config_file(self):
        """Test config file path."""
        config = Config(
            email="test@example.com",
            server_url="https://syftbox.net",
            data_dir="/path/to/data"
        )
        
        expected = Path.home() / ".syftbox" / "config.json"
        assert config.config_file == expected
    
    def test_binary_path(self):
        """Test binary path."""
        config = Config(
            email="test@example.com",
            server_url="https://syftbox.net",
            data_dir="/path/to/data"
        )
        
        expected = Path.home() / ".local" / "bin" / "syftbox"
        assert config.binary_path == expected
    
    def test_save_and_load(self):
        """Test saving and loading configuration."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Mock home directory
            with patch('pathlib.Path.home', return_value=Path(tmp_dir)):
                config = Config(
                    email="test@example.com",
                    server_url="https://syftbox.net",
                    data_dir="/path/to/data",
                    refresh_token="test_refresh_token",
                    access_token="test_access_token"
                )
                
                # Save config
                config.save()
                
                # Verify file exists
                config_file = Path(tmp_dir) / ".syftbox" / "config.json"
                assert config_file.exists()
                
                # Load config
                loaded_config = Config.load()
                assert loaded_config is not None
                assert loaded_config.email == "test@example.com"
                assert loaded_config.server_url == "https://syftbox.net"
                assert loaded_config.data_dir == "/path/to/data"
                assert loaded_config.refresh_token == "test_refresh_token"
                assert loaded_config.access_token == "test_access_token"
    
    def test_load_nonexistent(self):
        """Test loading when config doesn't exist."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch('pathlib.Path.home', return_value=Path(tmp_dir)):
                config = Config.load()
                assert config is None
    
    def test_load_invalid_json(self):
        """Test loading invalid JSON."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch('pathlib.Path.home', return_value=Path(tmp_dir)):
                config_dir = Path(tmp_dir) / ".syftbox"
                config_dir.mkdir(parents=True)
                config_file = config_dir / "config.json"
                
                # Write invalid JSON
                config_file.write_text("invalid json")
                
                config = Config.load()
                assert config is None
    
    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = Config(
            email="test@example.com",
            server_url="https://syftbox.net",
            data_dir="/path/to/data",
            refresh_token="test_refresh_token"
        )
        
        data = config.to_dict()
        assert data["email"] == "test@example.com"
        assert data["server_url"] == "https://syftbox.net"
        assert data["data_dir"] == "/path/to/data"
        assert data["refresh_token"] == "test_refresh_token"
        assert "access_token" not in data  # None values excluded
    
    def test_to_dict_with_access_token(self):
        """Test converting config with access token to dictionary."""
        config = Config(
            email="test@example.com",
            server_url="https://syftbox.net",
            data_dir="/path/to/data",
            refresh_token="test_refresh_token",
            access_token="test_access_token"
        )
        
        data = config.to_dict()
        assert data["access_token"] == "test_access_token"
    
    def test_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            "email": "test@example.com",
            "server_url": "https://syftbox.net",
            "data_dir": "/path/to/data",
            "refresh_token": "test_refresh_token",
            "access_token": "test_access_token"
        }
        
        config = Config.from_dict(data)
        assert config.email == "test@example.com"
        assert config.server_url == "https://syftbox.net"
        assert config.data_dir == "/path/to/data"
        assert config.refresh_token == "test_refresh_token"
        assert config.access_token == "test_access_token"
    
    def test_from_dict_missing_required(self):
        """Test creating config from dictionary with missing required fields."""
        data = {
            "email": "test@example.com"
            # Missing required fields
        }
        
        with pytest.raises(KeyError):
            Config.from_dict(data)
    
    def test_save_creates_directory(self):
        """Test that save creates the config directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch('pathlib.Path.home', return_value=Path(tmp_dir)):
                config = Config(
                    email="test@example.com",
                    server_url="https://syftbox.net",
                    data_dir="/path/to/data",
                    refresh_token="test_token"
                )
                
                # Directory shouldn't exist yet
                config_dir = Path(tmp_dir) / ".syftbox"
                assert not config_dir.exists()
                
                # Save should create it
                config.save()
                assert config_dir.exists()
                assert config_dir.is_dir()