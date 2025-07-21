#!/usr/bin/env python3
"""
Test harness for SyftBox authentication.
This script tests the OTP authentication flow step by step.
"""

import sys
import time
from syft_installer.auth import Authenticator
from syft_installer.validators import validate_email, validate_otp

def test_auth_flow():
    """Test the authentication flow interactively."""
    print("=== SyftBox Authentication Test ===\n")
    
    # Test server URL
    server_url = "https://syftbox.net"  # The correct server URL
    print(f"Server URL: {server_url}")
    
    # Create authenticator
    auth = Authenticator(server_url=server_url)
    print(f"✓ Authenticator created\n")
    
    # Get email from user
    while True:
        email = input("Enter your email address: ").strip()
        if validate_email(email):
            break
        print("❌ Invalid email address. Please try again.")
    
    print(f"\n📧 Email: {email}")
    
    # Test OTP request
    print("\n--- Testing OTP Request ---")
    try:
        print(f"Requesting OTP for {email}...")
        result = auth.request_otp(email)
        print("✅ OTP request successful!")
        print(f"Response: {result}")
        print("\n⏳ Check your email for the OTP code (including spam folder)")
    except Exception as e:
        print(f"❌ OTP request failed: {e}")
        return False
    
    # Get OTP from user
    print("\n--- Testing OTP Verification ---")
    while True:
        otp = input("Enter the 8-character OTP from your email: ").strip().upper()
        if validate_otp(otp):
            break
        print("❌ Invalid OTP. Must be exactly 8 uppercase letters/numbers.")
    
    # Test OTP verification
    try:
        print(f"\nVerifying OTP: {otp}")
        tokens = auth.verify_otp(email, otp)
        print("✅ OTP verification successful!")
        print(f"\nTokens received:")
        print(f"  Access Token: {tokens['access_token'][:50]}...")
        print(f"  Refresh Token: {tokens['refresh_token'][:50]}...")
        
        # Decode token to see claims
        claims = auth.decode_token(tokens['access_token'])
        print(f"\nToken claims:")
        print(f"  Email: {claims.get('sub', 'N/A')}")
        print(f"  Type: {claims.get('type', 'N/A')}")
        print(f"  Expires: {claims.get('exp', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ OTP verification failed: {e}")
        return False

def test_endpoints():
    """Test that endpoints are reachable."""
    import requests
    
    print("=== Testing Endpoint Connectivity ===\n")
    
    endpoints = [
        "https://syftbox.net",
        "https://syftbox.net/auth/otp/request",
        "https://syftbox.net/auth/otp/verify",
        "https://syftbox.net/auth/refresh",
    ]
    
    for endpoint in endpoints:
        try:
            # Just test connectivity, don't worry about response
            response = requests.head(endpoint, timeout=5, allow_redirects=True)
            print(f"✅ {endpoint} - Status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint} - Connection failed")
        except requests.exceptions.Timeout:
            print(f"⏱️  {endpoint} - Timeout")
        except Exception as e:
            print(f"❓ {endpoint} - Error: {type(e).__name__}")

if __name__ == "__main__":
    # First test endpoint connectivity
    test_endpoints()
    
    print("\n" + "="*50 + "\n")
    
    # Then test auth flow
    success = test_auth_flow()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)