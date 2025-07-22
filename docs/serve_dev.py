#!/usr/bin/env python3
"""
Development server for syft-installer documentation with hot reloading.
"""

import os
import sys
import time
import threading
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import subprocess

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("Installing required dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "watchdog"])
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler


class LiveReloadHandler(SimpleHTTPRequestHandler):
    """HTTP handler with live reload injection."""
    
    def end_headers(self):
        if self.path.endswith('.html'):
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        super().end_headers()
    
    def do_GET(self):
        if self.path == '/livereload':
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Keep connection open and wait for reload signal
            while True:
                if hasattr(self.server, 'reload_flag') and self.server.reload_flag:
                    self.wfile.write(b'data: reload\n\n')
                    self.wfile.flush()
                    self.server.reload_flag = False
                    break
                time.sleep(0.1)
            return
        
        # Inject live reload script into HTML files
        if self.path.endswith('.html') or self.path == '/':
            # Get the file path
            if self.path == '/':
                file_path = 'index.html'
            else:
                file_path = self.path.lstrip('/')
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Inject live reload script before closing body tag
                live_reload_script = """
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
                
                content = content.replace('</body>', live_reload_script)
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(content.encode('utf-8'))))
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
                return
            except FileNotFoundError:
                pass
        
        # Default behavior for other files
        super().do_GET()


class FileWatcher(FileSystemEventHandler):
    """Watch for file changes and trigger reload."""
    
    def __init__(self, server):
        self.server = server
        self.last_modified = {}
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Only watch relevant files
        if any(event.src_path.endswith(ext) for ext in ['.html', '.css', '.js', '.svg', '.png', '.jpg', '.gif']):
            # Debounce - ignore if file was just modified
            current_time = time.time()
            if event.src_path in self.last_modified:
                if current_time - self.last_modified[event.src_path] < 0.5:
                    return
            
            self.last_modified[event.src_path] = current_time
            print(f"File changed: {event.src_path}")
            self.server.reload_flag = True


def run_server(port=8000):
    """Run the development server with hot reloading."""
    # Change to docs directory
    docs_dir = Path(__file__).parent
    os.chdir(docs_dir)
    
    # Create HTTP server
    server = HTTPServer(('localhost', port), LiveReloadHandler)
    server.reload_flag = False
    
    # Set up file watcher
    event_handler = FileWatcher(server)
    observer = Observer()
    observer.schedule(event_handler, '.', recursive=True)
    observer.start()
    
    # Open browser
    url = f'http://localhost:{port}'
    print(f"\n🚀 Development server running at {url}")
    print("📁 Serving from: {0}".format(os.getcwd()))
    print("👀 Watching for file changes...")
    print("\nPress Ctrl+C to stop\n")
    
    # Wait a moment then open browser
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down server...")
        observer.stop()
        observer.join()
        server.shutdown()
        print("✅ Server stopped\n")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Development server for syft-installer docs')
    parser.add_argument('-p', '--port', type=int, default=8000, help='Port to run server on (default: 8000)')
    args = parser.parse_args()
    
    run_server(args.port)
</script>
</body>"""
                
                content = content.replace('</body>', live_reload_script)
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(content.encode('utf-8'))))
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
                return
            except FileNotFoundError:
                pass
        
        # Default behavior for other files
        super().do_GET()


class FileWatcher(FileSystemEventHandler):
    """Watch for file changes and trigger reload."""
    
    def __init__(self, server):
        self.server = server
        self.last_modified = {}
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Only watch relevant files
        if any(event.src_path.endswith(ext) for ext in ['.html', '.css', '.js', '.svg', '.png', '.jpg', '.gif']):
            # Debounce - ignore if file was just modified
            current_time = time.time()
            if event.src_path in self.last_modified:
                if current_time - self.last_modified[event.src_path] < 0.5:
                    return
            
            self.last_modified[event.src_path] = current_time
            print(f"File changed: {event.src_path}")
            self.server.reload_flag = True


def run_server(port=8000):
    """Run the development server with hot reloading."""
    # Change to docs directory
    docs_dir = Path(__file__).parent
    os.chdir(docs_dir)
    
    # Create HTTP server
    server = HTTPServer(('localhost', port), LiveReloadHandler)
    server.reload_flag = False
    
    # Set up file watcher
    event_handler = FileWatcher(server)
    observer = Observer()
    observer.schedule(event_handler, '.', recursive=True)
    observer.start()
    
    # Open browser
    url = f'http://localhost:{port}'
    print(f"\n🚀 Development server running at {url}")
    print("📁 Serving from: {0}".format(os.getcwd()))
    print("👀 Watching for file changes...")
    print("\nPress Ctrl+C to stop\n")
    
    # Wait a moment then open browser
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down server...")
        observer.stop()
        observer.join()
        server.shutdown()
        print("✅ Server stopped\n")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Development server for syft-installer docs')
    parser.add_argument('-p', '--port', type=int, default=8000, help='Port to run server on (default: 8000)')
    args = parser.parse_args()
    
    run_server(args.port)