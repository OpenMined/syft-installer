#!/usr/bin/env python3
"""
Simple script to test the OTP authentication flow.
"""

import syft_installer as si

def test_simple_install():
    """Test the simplest installation flow."""
    print("=== Testing Simple Installation Flow ===\n")
    print("This will:")
    print("1. Download the SyftBox binary")
    print("2. Request an OTP to your email")
    print("3. Create configuration after OTP verification")
    print("4. Start the SyftBox client\n")
    
    # Get email from user
    email = input("Enter your email address: ").strip()
    
    print(f"\nStarting installation for: {email}")
    
    # Create installer with email
    installer = si.Installer(email=email)
    
    try:
        # Run installation
        installer.install()
        print("\n✅ Installation complete!")
        
    except Exception as e:
        print(f"\n❌ Installation failed: {e}")
        import traceback
        traceback.print_exc()

def test_step_by_step():
    """Test step-by-step installation."""
    print("=== Testing Step-by-Step Installation ===\n")
    
    # Get email
    email = input("Enter your email address: ").strip()
    
    # Create installer
    installer = si.Installer(email=email)
    
    try:
        # Step 1: Download binary
        print("\n📥 Downloading binary...")
        installer.download_binary()
        print("✅ Download complete")
        
        # Step 2: Setup environment
        print("\n🔧 Setting up environment...")
        installer.setup_environment()
        print("✅ Environment ready")
        
        # Step 3: Request OTP
        print(f"\n📧 Requesting OTP for {email}...")
        installer.request_otp()
        print("✅ OTP sent! Check your email (including spam)")
        
        # Step 4: Get and verify OTP
        otp = input("\nEnter the 8-character OTP from email: ").strip()
        print(f"\n🔐 Verifying OTP: {otp.upper()}")
        installer.verify_otp(otp)
        print("✅ Authentication successful!")
        
        # Step 5: Start client
        start = input("\nStart SyftBox client? [Y/n]: ").strip().lower()
        if start != 'n':
            print("\n🚀 Starting client...")
            installer.start_client(background=True)
            print("✅ Client started in background")
        
        print("\n✅ Installation complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    
    print("SyftBox Installer - OTP Flow Test")
    print("=" * 50)
    print("\nChoose test mode:")
    print("1. Simple install (one command)")
    print("2. Step-by-step install")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        test_simple_install()
    elif choice == "2":
        test_step_by_step()
    else:
        print("Exiting...")
        sys.exit(0)