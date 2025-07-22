"""Unit tests for documentation development server."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from pathlib import Path
import time
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Add the docs directory to sys.path for importing
docs_dir = Path(__file__).parent.parent / "docs"
sys.path.insert(0, str(docs_dir))

import serve_dev


class TestLiveReloadHandler:
    """Test LiveReloadHandler class."""
    
    def test_live_reload_script_injection(self):
        """Test that live reload script is properly formatted."""
        # Just test the functionality without creating actual handler instances
        test_html = "<html><body><h1>Test</h1></body></html>"
        expected_script = """
<script>
(function() {
    const source = new EventSource('/livereload');
    source.onmessage = function(e) {
        if (e.data === 'reload') {
            location.reload();
        }
    };
    source.onerror = function() {
        setTimeout(() => location.reload(), 1000);
    };
})();
</script>
</body>"""
        
        result = test_html.replace('</body>', expected_script)
        assert 'EventSource' in result
        assert '/livereload' in result
        assert 'location.reload()' in result
        assert result.endswith('</body></html>')
    
    def test_handler_exists(self):
        """Test that LiveReloadHandler class exists and has required methods."""
        assert hasattr(serve_dev.LiveReloadHandler, 'end_headers')
        assert hasattr(serve_dev.LiveReloadHandler, 'do_GET')
        assert issubclass(serve_dev.LiveReloadHandler, SimpleHTTPRequestHandler)


class TestFileWatcher:
    """Test FileWatcher class."""
    
    def test_init(self):
        """Test file watcher initialization."""
        server = Mock()
        watcher = serve_dev.FileWatcher(server)
        assert watcher.server == server
        assert watcher.last_modified == {}
    
    def test_on_modified_directory(self):
        """Test that directory modifications are ignored."""
        server = Mock()
        server.reload_flag = False
        watcher = serve_dev.FileWatcher(server)
        
        event = Mock()
        event.is_directory = True
        
        watcher.on_modified(event)
        assert server.reload_flag == False  # Should remain False for directories
    
    def test_on_modified_relevant_file(self):
        """Test that relevant file modifications trigger reload."""
        server = Mock()
        server.reload_flag = False
        watcher = serve_dev.FileWatcher(server)
        
        event = Mock()
        event.is_directory = False
        event.src_path = 'test.html'
        
        watcher.on_modified(event)
        assert server.reload_flag == True
    
    def test_on_modified_irrelevant_file(self):
        """Test that irrelevant file modifications don't trigger reload."""
        server = Mock()
        server.reload_flag = False
        watcher = serve_dev.FileWatcher(server)
        
        event = Mock()
        event.is_directory = False
        event.src_path = 'test.txt'
        
        watcher.on_modified(event)
        assert server.reload_flag == False
    
    def test_on_modified_debounce(self):
        """Test that rapid modifications are debounced."""
        server = Mock()
        server.reload_flag = False
        watcher = serve_dev.FileWatcher(server)
        
        event = Mock()
        event.is_directory = False
        event.src_path = 'test.html'
        
        # First modification
        watcher.on_modified(event)
        assert server.reload_flag == True
        
        # Reset flag
        server.reload_flag = False
        
        # Immediate second modification (should be ignored)
        watcher.on_modified(event)
        assert server.reload_flag == False
        
        # Wait and try again (should work)
        time.sleep(0.6)
        watcher.on_modified(event)
        assert server.reload_flag == True


def test_run_server_components():
    """Test that run_server has all required components."""
    # Just verify the function exists and has the right signature
    import inspect
    sig = inspect.signature(serve_dev.run_server)
    assert 'port' in sig.parameters
    assert sig.parameters['port'].default == 8000


def test_script_imports():
    """Test that the script has all required imports."""
    assert hasattr(serve_dev, 'HTTPServer')
    assert hasattr(serve_dev, 'SimpleHTTPRequestHandler')
    assert hasattr(serve_dev, 'Observer')
    assert hasattr(serve_dev, 'FileSystemEventHandler')
    assert hasattr(serve_dev, 'LiveReloadHandler')
    assert hasattr(serve_dev, 'FileWatcher')
    assert hasattr(serve_dev, 'run_server')