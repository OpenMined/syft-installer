#!/usr/bin/env python3
"""
Simple HTTP server for syft-installer documentation (no live reload).
"""

import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

def run_server(port=8000):
    """Run a simple HTTP server."""
    # Change to docs directory
    docs_dir = Path(__file__).parent
    os.chdir(docs_dir)
    
    print(f"\n🚀 Simple server running at http://localhost:{port}")
    print("📁 Serving from: {0}".format(os.getcwd()))
    print("\nPress Ctrl+C to stop\n")
    
    try:
        server = HTTPServer(('localhost', port), SimpleHTTPRequestHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped\n")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Simple server for syft-installer docs')
    parser.add_argument('-p', '--port', type=int, default=8000, help='Port to run server on (default: 8000)')
    args = parser.parse_args()
    
    run_server(args.port)