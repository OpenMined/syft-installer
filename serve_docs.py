#!/usr/bin/env python3
"""
Simple static server for syft-installer documentation.
Serves docs exactly as GitHub Pages would.
"""

import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

def main():
    # Change to docs directory
    docs_dir = os.path.join(os.path.dirname(__file__), 'docs')
    os.chdir(docs_dir)
    
    # Use port 8000 by default
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port: {sys.argv[1]}")
            sys.exit(1)
    
    # Start server
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    
    print(f"\n📁 Serving docs from: {os.getcwd()}")
    print(f"🌐 Server running at: http://localhost:{port}/")
    print("\nPress Ctrl-C to stop\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")

if __name__ == '__main__':
    main()