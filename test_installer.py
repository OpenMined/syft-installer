#!/usr/bin/env python3
"""
Test the full installer flow.
"""

import os
import sys
import time
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import syft_installer as si
from syft_installer.exceptions import *

def test_basic_functionality():
    """Test basic functionality without actually installing."""
    print("=== Testing Basic Functionality ===\n")
    
    # Test 1: Check installation status
    print("1. Checking installation status...")
    try:
        is_installed = si.is_installed()
        print(f"   Is installed: {is_installed}")
        
        if is_installed:
            config = si.load_config()
            if config:
                print(f"   Email: {config.email}")
                print(f"   Server: {config.server_url}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Check if running
    print("\n2. Checking if client is running...")
    try:
        is_running = si.is_running()
        print(f"   Is running: {is_running}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Platform detection
    print("\n3. Testing platform detection...")
    try:
        from syft_installer.platform import get_platform_info, get_binary_url
        os_name, arch = get_platform_info()
        print(f"   OS: {os_name}")
        print(f"   Architecture: {arch}")
        print(f"   Binary URL: {get_binary_url()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Runtime environment
    print("\n4. Testing runtime environment...")
    try:
        from syft_installer.runtime import RuntimeEnvironment
        runtime = RuntimeEnvironment()
        print(f"   Is notebook: {runtime.is_notebook}")
        print(f"   Is Colab: {runtime.is_colab}")
        print(f"   Has TTY: {runtime.has_tty}")
        print(f"   Default data dir: {runtime.default_data_dir}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ Basic functionality tests complete!")

def test_installer_creation():
    """Test creating installer instances."""
    print("\n=== Testing Installer Creation ===\n")
    
    # Test 1: Default installer
    print("1. Creating default installer...")
    try:
        installer = si.Installer()
        print("   ✅ Default installer created")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Installer with email
    print("\n2. Creating installer with email...")
    try:
        installer = si.Installer(email="test@example.com")
        print(f"   ✅ Installer created with email: {installer.email}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Installer with custom server
    print("\n3. Creating installer with custom server...")
    try:
        installer = si.Installer(
            email="test@example.com",
            server_url="https://custom.server.com"
        )
        print(f"   ✅ Installer created with server: {installer.server_url}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Headless installer
    print("\n4. Creating headless installer...")
    try:
        installer = si.Installer(
            email="test@example.com",
            headless=True
        )
        print("   ✅ Headless installer created")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n✅ Installer creation tests complete!")

def test_auth_components():
    """Test authentication components."""
    print("\n=== Testing Authentication Components ===\n")
    
    # Test 1: Email validation
    print("1. Testing email validation...")
    from syft_installer.validators import validate_email
    
    test_emails = [
        ("valid@example.com", True),
        ("user.name@company.co.uk", True),
        ("invalid", False),
        ("@example.com", False),
        ("user@", False),
        ("", False),
    ]
    
    for email, expected in test_emails:
        result = validate_email(email)
        status = "✅" if result == expected else "❌"
        print(f"   {status} '{email}' -> {result} (expected {expected})")
    
    # Test 2: OTP validation
    print("\n2. Testing OTP validation...")
    from syft_installer.validators import validate_otp, sanitize_otp
    
    test_otps = [
        ("ABCD1234", True),
        ("12345678", True),
        ("AAAAAAAA", True),
        ("abcd1234", False),  # lowercase
        ("ABCD123", False),   # too short
        ("ABCD12345", False), # too long
        ("ABCD-1234", False), # invalid char
        ("", False),
    ]
    
    for otp, expected in test_otps:
        result = validate_otp(otp)
        status = "✅" if result == expected else "❌"
        print(f"   {status} '{otp}' -> {result} (expected {expected})")
    
    # Test 3: OTP sanitization
    print("\n3. Testing OTP sanitization...")
    test_sanitize = [
        ("abcd1234", "ABCD1234"),
        (" ABCD1234 ", "ABCD1234"),
        ("ab cd 12 34", "ABCD1234"),
    ]
    
    for input_otp, expected in test_sanitize:
        result = sanitize_otp(input_otp)
        status = "✅" if result == expected else "❌"
        print(f"   {status} '{input_otp}' -> '{result}' (expected '{expected}')")
    
    print("\n✅ Authentication component tests complete!")

def test_download_url():
    """Test that the download URL is correct."""
    print("\n=== Testing Download URL ===\n")
    
    from syft_installer.platform import get_binary_url
    import requests
    
    url = get_binary_url()
    print(f"Binary URL: {url}")
    
    # Test if URL is reachable
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code == 200:
            print("✅ Binary URL is valid and reachable")
            print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
            print(f"   Content-Length: {response.headers.get('content-length', 'N/A')} bytes")
        else:
            print(f"⚠️  Binary URL returned status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to reach binary URL: {e}")

def main():
    """Run all tests."""
    print("SyftBox Installer Test Suite")
    print("=" * 50)
    
    test_basic_functionality()
    test_installer_creation()
    test_auth_components()
    test_download_url()
    
    print("\n" + "=" * 50)
    print("All tests complete!")
    
    # Final summary
    print("\nTo test the full installation flow interactively:")
    print("1. Run: python3 -c 'import syft_installer as si; si.install()'")
    print("2. Enter your email when prompted")
    print("3. Check your email for the OTP")
    print("4. Enter the OTP when prompted")
    print("\nOr use the step-by-step approach in the tutorial notebook.")

if __name__ == "__main__":
    main()