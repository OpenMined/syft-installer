"""Unit tests for launcher module."""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
import subprocess
from pathlib import Path

from syft_installer._launcher import Launcher, start_client, stop_client, restart_client, is_running
from syft_installer._config import Config
from syft_installer._exceptions import BinaryNotFoundError


class TestLauncher:
    """Test Launcher class."""
    
    def test_init(self):
        """Test launcher initialization."""
        launcher = Launcher()
        assert launcher.process is None
        # Launcher doesn't use threads anymore
    
    @patch('subprocess.Popen')
    def test_start_foreground(self, mock_popen):
        """Test starting client in foreground."""
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process
        
        config = Config(
            email="test@example.com",
            server_url="https://syftbox.net",
            data_dir="/test/data"
        )
        
        with patch.object(Path, 'exists', return_value=True):
            launcher = Launcher()
            launcher.start(config, background=False)
            
            mock_popen.assert_called_once_with([
                str(config.binary_path),
                "daemon"
            ])
            mock_process.wait.assert_called_once()
    
    @patch('threading.Thread')
    @patch('subprocess.Popen')
    def test_start_background(self, mock_popen, mock_thread):
        """Test starting client in background."""
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process
        
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        
        config = Config(
            email="test@example.com",
            server_url="https://syftbox.net",
            data_dir="/test/data"
        )
        
        with patch.object(Path, 'exists', return_value=True):
            launcher = Launcher()
            launcher.start(config, background=True)
            
            mock_thread.assert_called_once()
            mock_thread_instance.start.assert_called_once()
            assert mock_thread_instance.daemon is True
    
    def test_start_binary_not_found(self):
        """Test starting when binary doesn't exist."""
        config = Config(
            email="test@example.com",
            server_url="https://syftbox.net",
            data_dir="/test/data"
        )
        
        with patch.object(Path, 'exists', return_value=False):
            launcher = Launcher()
            with pytest.raises(BinaryNotFoundError):
                launcher.start(config)
    
    def test_start_already_running(self):
        """Test starting when already running."""
        config = Config(
            email="test@example.com",
            server_url="https://syftbox.net",
            data_dir="/test/data"
        )
        
        launcher = Launcher()
        launcher.process = Mock()
        launcher.process.poll.return_value = None  # Still running
        
        with patch.object(Path, 'exists', return_value=True):
            with patch('subprocess.Popen') as mock_popen:
                launcher.start(config)
                mock_popen.assert_not_called()  # Should not start again
    
    def test_stop(self):
        """Test stopping the client."""
        mock_process = Mock()
        mock_process.poll.return_value = None  # Still running
        
        launcher = Launcher()
        launcher.process = mock_process
        
        launcher.stop()
        
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once_with(timeout=5)
        assert launcher.process is None
    
    def test_stop_timeout(self):
        """Test stopping with timeout."""
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_process.wait.side_effect = subprocess.TimeoutExpired("cmd", 5)
        
        launcher = Launcher()
        launcher.process = mock_process
        
        launcher.stop()
        
        mock_process.terminate.assert_called_once()
        mock_process.kill.assert_called_once()
        assert mock_process.wait.call_count == 2
    
    def test_stop_not_running(self):
        """Test stopping when not running."""
        launcher = Launcher()
        launcher.stop()  # Should not raise error
    
    @patch.object(Launcher, 'stop')
    @patch.object(Launcher, 'start')
    @patch('time.sleep')
    def test_restart(self, mock_sleep, mock_start, mock_stop):
        """Test restarting the client."""
        config = Config(
            email="test@example.com",
            server_url="https://syftbox.net",
            data_dir="/test/data"
        )
        
        launcher = Launcher()
        launcher.restart(config)
        
        mock_stop.assert_called_once()
        mock_sleep.assert_called_once_with(1)
        mock_start.assert_called_once_with(config)
    
    def test_is_running_with_process(self):
        """Test checking if running with active process."""
        mock_process = Mock()
        mock_process.poll.return_value = None  # Still running
        
        launcher = Launcher()
        launcher.process = mock_process
        
        assert launcher.is_running() is True
    
    def test_is_running_process_exited(self):
        """Test checking if running with exited process."""
        mock_process = Mock()
        mock_process.poll.return_value = 0  # Exited
        
        launcher = Launcher()
        launcher.process = mock_process
        
        # Mock pgrep to return no results
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            assert launcher.is_running() is False
    
    @patch('subprocess.run')
    def test_is_running_external_process(self, mock_run):
        """Test checking for external syftbox process."""
        # Mock pgrep finding a process
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "12345\n"
        
        launcher = Launcher()
        assert launcher.is_running() is True
        
        mock_run.assert_called_once_with(
            ["pgrep", "-f", "syftbox"],
            capture_output=True,
            text=True
        )
    
    @patch('subprocess.run')
    def test_is_running_no_external_process(self, mock_run):
        """Test checking when no external process exists."""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        
        launcher = Launcher()
        assert launcher.is_running() is False
    
    def test_get_status(self):
        """Test getting status."""
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_process.pid = 12345
        
        launcher = Launcher()
        launcher.process = mock_process
        
        status = launcher.get_status()
        assert status["running"] is True
        assert status["pid"] == 12345
    
    def test_get_status_not_running(self):
        """Test getting status when not running."""
        launcher = Launcher()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            status = launcher.get_status()
            assert status["running"] is False
            assert status["pid"] is None


class TestModuleFunctions:
    """Test module-level convenience functions."""
    
    @patch('syft_installer._launcher._launcher.start')
    @patch('syft_installer._config.Config.load')
    def test_start_client_with_config(self, mock_load, mock_start):
        """Test start_client with provided config."""
        config = Config(
            email="test@example.com",
            server_url="https://syftbox.net",
            data_dir="/test/data"
        )
        
        start_client(config, background=True)
        
        mock_load.assert_not_called()
        mock_start.assert_called_once_with(config, True)
    
    @patch('syft_installer._launcher._launcher.start')
    @patch('syft_installer._config.Config.load')
    def test_start_client_load_config(self, mock_load, mock_start):
        """Test start_client loading config."""
        config = Config(
            email="test@example.com",
            server_url="https://syftbox.net",
            data_dir="/test/data"
        )
        mock_load.return_value = config
        
        start_client()
        
        mock_load.assert_called_once()
        mock_start.assert_called_once_with(config, False)
    
    @patch('syft_installer._config.Config.load')
    def test_start_client_no_config(self, mock_load):
        """Test start_client with no config found."""
        mock_load.return_value = None
        
        with pytest.raises(ValueError, match="No configuration found"):
            start_client()
    
    @patch('syft_installer._launcher._launcher.stop')
    def test_stop_client(self, mock_stop):
        """Test stop_client."""
        stop_client()
        mock_stop.assert_called_once()
    
    @patch('syft_installer._launcher._launcher.restart')
    @patch('syft_installer._config.Config.load')
    def test_restart_client(self, mock_load, mock_restart):
        """Test restart_client."""
        config = Config(
            email="test@example.com",
            server_url="https://syftbox.net",
            data_dir="/test/data"
        )
        mock_load.return_value = config
        
        restart_client()
        
        mock_load.assert_called_once()
        mock_restart.assert_called_once_with(config)
    
    @patch('syft_installer._launcher._launcher.is_running')
    def test_is_running_function(self, mock_is_running):
        """Test is_running function."""
        mock_is_running.return_value = True
        
        result = is_running()
        assert result is True
        mock_is_running.assert_called_once()