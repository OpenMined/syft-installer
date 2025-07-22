"""Utilities for Google Colab integration."""
import os
import subprocess
from typing import Optional


def is_google_colab() -> bool:
    """Check if we're running in Google Colab."""
    try:
        import google.colab
        return True
    except ImportError:
        return False


def get_colab_user_email() -> Optional[str]:
    """
    Get the authenticated user's email in Google Colab.
    
    Returns:
        Email address if in Colab and authenticated, None otherwise
    """
    if not is_google_colab():
        return None
        
    try:
        # Import here to avoid import errors outside Colab
        import requests
        from google.colab import auth
        
        print("🔐 Authenticating with Google account...")
        # Authenticate the user with a Google account
        auth.authenticate_user()
        
        # Get the Google Cloud access token using subprocess
        result = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            check=True
        )
        gcloud_token = result.stdout.strip()
        
        # Use the access token to get information about the token
        response = requests.get(
            'https://www.googleapis.com/oauth2/v3/tokeninfo',
            params={'access_token': gcloud_token}
        )
        
        if response.status_code == 200:
            tokeninfo = response.json()
            email = tokeninfo.get('email')
            if email:
                print(f"✅ Detected email: {email}")
                return email
        
        print("❌ Could not detect email from Google account")
        return None
        
    except subprocess.CalledProcessError:
        print("❌ Failed to get gcloud access token")
        return None
    except requests.RequestException as e:
        print(f"❌ Failed to get token info: {e}")
        return None
    except Exception as e:
        print(f"❌ Error during Colab authentication: {e}")
        return None