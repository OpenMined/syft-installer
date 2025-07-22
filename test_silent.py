#!/usr/bin/env python3
"""Test silent mode functionality."""

import syft_installer as si
import sys
from io import StringIO

# Test status with silent mode
print("Testing status(silent=True)...")
old_stdout = sys.stdout
stdout_buffer = StringIO()
sys.stdout = stdout_buffer

result = si.status(silent=True)
sys.stdout = old_stdout
output = stdout_buffer.getvalue()

if output:
    print(f"FAILED: Got output: {repr(output)}")
else:
    print("PASSED: No output in silent mode")

print(f"Result: {result}")

# Test run with silent mode (if installed)
if result['installed']:
    print("\nTesting run(silent=True)...")
    old_stdout = sys.stdout
    stdout_buffer = StringIO()
    sys.stdout = stdout_buffer
    
    success = si.run(silent=True)
    sys.stdout = old_stdout
    output = stdout_buffer.getvalue()
    
    if output:
        print(f"FAILED: Got output: {repr(output)}")
    else:
        print("PASSED: No output in silent mode")
    
    print(f"Result: {success}")

print("\nSilent mode tests complete!")