"""Unit tests for process management module."""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
import subprocess
from pathlib import Path

from syft_installer._process import ProcessManager
from syft_installer._config import Config
from syft_installer._exceptions import BinaryNotFoundError


class TestProcessManager:
    """Test ProcessManager class."""
    
    def test_init(self):
        """Test process manager initialization."""
        pm = ProcessManager()
        assert pm.process is None
    
    @patch('syft_installer._process.ProcessManager._run_foreground')
    def test_start_foreground(self, mock_run_fg):
        """Test starting client in foreground."""
        config = Config(
            email="test@example.com",
            server_url="https://syftbox.net",
            data_dir="/test/data"
        )
        
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(ProcessManager, 'is_running', return_value=False):
                pm = ProcessManager()
                pm.start(config, background=False)
                
                mock_run_fg.assert_called_once()
    
    @patch('syft_installer._process.ProcessManager._run_background')
    def test_start_background(self, mock_run_bg):
        """Test starting client in background."""
        config = Config(
            email="test@example.com",
            server_url="https://syftbox.net",
            data_dir="/test/data"
        )
        
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(ProcessManager, 'is_running', return_value=False):
                pm = ProcessManager()
                pm.start(config, background=True)
                
                mock_run_bg.assert_called_once()
    
    def test_start_binary_not_found(self):
        """Test starting when binary doesn't exist."""
        config = Config(
            email="test@example.com",
            server_url="https://syftbox.net",
            data_dir="/test/data"
        )
        
        with patch.object(Path, 'exists', return_value=False):
            pm = ProcessManager()
            with pytest.raises(BinaryNotFoundError):
                pm.start(config)
    
    def test_start_already_running(self):
        """Test starting when already running."""
        config = Config(
            email="test@example.com",
            server_url="https://syftbox.net",
            data_dir="/test/data"
        )
        
        pm = ProcessManager()
        pm.process = Mock()
        pm.process.poll.return_value = None  # Still running
        
        with patch.object(Path, 'exists', return_value=True):
            with patch('syft_installer._process.ProcessManager._run_background') as mock_run:
                pm.start(config)
                mock_run.assert_not_called()  # Should not start again
    
    def test_stop(self):
        """Test stopping the client."""
        mock_process = Mock()
        mock_process.poll.return_value = None  # Still running
        
        pm = ProcessManager()
        pm.process = mock_process
        
        pm.stop()
        
        mock_process.terminate.assert_called_once()
    
    def test_stop_timeout(self):
        """Test stopping with timeout."""
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_process.wait.side_effect = subprocess.TimeoutExpired("cmd", 5)
        
        pm = ProcessManager()
        pm.process = mock_process
        
        pm.stop()
        
        mock_process.terminate.assert_called_once()
        mock_process.kill.assert_called_once()
    
    def test_stop_not_running(self):
        """Test stopping when not running."""
        pm = ProcessManager()
        pm.stop()  # Should not raise error
    
    def test_restart(self):
        """Test restarting the client - ProcessManager doesn't have restart method."""
        # ProcessManager doesn't have a restart method - this would be handled
        # at a higher level by calling stop() then start()
        pass
    
    def test_is_running_with_process(self):
        """Test checking if running with active process."""
        mock_process = Mock()
        mock_process.poll.return_value = None  # Still running
        
        pm = ProcessManager()
        pm.process = mock_process
        
        # ProcessManager.is_running() uses pgrep, not process state
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "12345\n"
            assert pm.is_running() is True
    
    def test_is_running_process_exited(self):
        """Test checking if running with exited process."""
        mock_process = Mock()
        mock_process.poll.return_value = 0  # Exited
        
        pm = ProcessManager()
        pm.process = mock_process
        
        # Mock pgrep to return no results
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            assert pm.is_running() is False
    
    @patch('subprocess.run')
    def test_is_running_external_process(self, mock_run):
        """Test checking for external syftbox process."""
        # Mock pgrep finding a process
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "12345\n"
        
        pm = ProcessManager()
        assert pm.is_running() is True
        
        mock_run.assert_called_once_with(
            ["pgrep", "-f", "syftbox daemon"],
            capture_output=True,
            text=True
        )
    
    @patch('subprocess.run')
    def test_is_running_no_external_process(self, mock_run):
        """Test checking when no external process exists."""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        
        pm = ProcessManager()
        assert pm.is_running() is False
    
    def test_find_daemons(self):
        """Test finding daemon processes."""
        pm = ProcessManager()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "USER       PID  %CPU %MEM    VSZ   RSS   TT  STAT STARTED      TIME COMMAND\nuser     12345   0.1  0.2 123456  7890   ??  S     1:23PM   0:01.23 /path/to/syftbox daemon\n"
            
            daemons = pm.find_daemons()
            assert len(daemons) > 0
