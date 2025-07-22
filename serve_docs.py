#!/usr/bin/env python3
"""
Convenience script to run the documentation development server.
"""

import subprocess
import sys
from pathlib import Path

# Get the path to the actual server script
docs_serve_script = Path(__file__).parent / "docs" / "serve_dev.py"

# Forward all arguments to the actual script
subprocess.run([sys.executable, str(docs_serve_script)] + sys.argv[1:])