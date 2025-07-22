#!/usr/bin/env python3
"""Test non-interactive installation mode."""

import syft_installer as si

# Test non-interactive install_and_run
print("Testing non-interactive install_and_run...")
print("=" * 50)

# This would be called from another app/service
session = si.install_and_run("test@example.com", interactive=False)

if session:
    print(f"\nSession created: {session}")
    print(f"OTP sent: {session._otp_sent}")
    print(f"Installation complete: {session.is_complete}")
    
    # In a real app, you'd get the OTP from the user somehow
    # For example, via a web form, API call, etc.
    # otp = get_otp_from_user()  
    # result = session.submit_otp(otp)
    # print(f"Result: {result}")
else:
    print("Already installed or error occurred")

print("\n" + "=" * 50)
print("Testing non-interactive install...")

# Test non-interactive install only
session2 = si.install("test2@example.com", interactive=False)

if session2:
    print(f"\nSession created: {session2}")
    print(f"OTP sent: {session2._otp_sent}")
    print(f"Installation complete: {session2.is_complete}")
    # session2.submit_otp("ABC12345")
else:
    print("Already installed or error occurred")