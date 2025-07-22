import json
from typing import Dict, Optional

import jwt
import requests

from syft_installer._exceptions import AuthenticationError, ValidationError
from syft_installer._validators import validate_email, validate_otp, sanitize_otp


class Authenticator:
    """Handle OTP-based authentication flow."""
    
    def __init__(self, server_url: str = "https://syftbox.net"):
        self.server_url = server_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "syft-installer/0.3.1",
            "Content-Type": "application/json",
        })
    
    def request_otp(self, email: str) -> Dict[str, str]:
        """
        Request OTP to be sent to email.
        
        Args:
            email: User's email address
            
        Returns:
            Response data from server
            
        Raises:
            ValidationError: If email is invalid
            AuthenticationError: If request fails
        """
        if not validate_email(email):
            raise ValidationError(f"Invalid email address: {email}")
        
        url = f"{self.server_url}/auth/otp/request"
        data = {"email": email}
        
        print(f"🌐 Making request to: {url}")
        print(f"📧 With email: {email}")
        
        try:
            response = self.session.post(url, json=data, timeout=30)
            print(f"📡 Response status: {response.status_code}")
            print(f"📡 Response headers: {dict(response.headers)}")
            response.raise_for_status()
            
            # OTP request returns empty body on success
            return {"status": "success", "message": "OTP sent to email"}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request exception: {type(e).__name__}")
            print(f"❌ Exception details: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error', str(e))
                    raise AuthenticationError(f"Failed to request OTP: {error_msg}")
                except:
                    pass
            raise AuthenticationError(f"Failed to request OTP: {str(e)}")
    
    def verify_otp(self, email: str, otp: str) -> Dict[str, str]:
        """
        Verify OTP and get authentication tokens.
        
        Args:
            email: User's email address
            otp: 8-character OTP code
            
        Returns:
            Dict containing access_token and refresh_token
            
        Raises:
            ValidationError: If email or OTP is invalid
            AuthenticationError: If verification fails
        """
        if not validate_email(email):
            raise ValidationError(f"Invalid email address: {email}")
        
        # Sanitize and validate OTP
        otp = sanitize_otp(otp)
        if not validate_otp(otp):
            raise ValidationError("Invalid OTP. Must be 8 uppercase alphanumeric characters.")
        
        url = f"{self.server_url}/auth/otp/verify"
        data = {"email": email, "code": otp}  # API expects "code" not "otp"
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            
            # Response format is {"accessToken": "...", "refreshToken": "..."}
            if "accessToken" not in result or "refreshToken" not in result:
                raise AuthenticationError("Invalid response: missing tokens")
            
            # Convert to snake_case for consistency
            return {
                "access_token": result["accessToken"],
                "refresh_token": result["refreshToken"]
            }
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 401:
                    raise AuthenticationError("Invalid OTP or expired")
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error', str(e))
                    raise AuthenticationError(f"Failed to verify OTP: {error_msg}")
                except:
                    pass
            raise AuthenticationError(f"Failed to verify OTP: {str(e)}")
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Use refresh token to get new tokens.
        
        Args:
            refresh_token: JWT refresh token
            
        Returns:
            Dict with new access_token and refresh_token
            
        Raises:
            AuthenticationError: If refresh fails
        """
        url = f"{self.server_url}/auth/refresh"
        data = {"refreshToken": refresh_token}
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            
            # Convert to snake_case
            return {
                "access_token": result["accessToken"],
                "refresh_token": result["refreshToken"]
            }
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 401:
                    raise AuthenticationError("Refresh token expired or invalid")
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error', str(e))
                    raise AuthenticationError(f"Failed to refresh token: {error_msg}")
                except:
                    pass
            raise AuthenticationError(f"Failed to refresh token: {str(e)}")
    
    @staticmethod
    def decode_token(token: str) -> Dict:
        """Decode JWT token without verification (for reading claims)."""
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except Exception:
            return {}
    
    @staticmethod
    def is_token_expired(token: str) -> bool:
        """Check if JWT token is expired."""
        try:
            claims = Authenticator.decode_token(token)
            if "exp" not in claims:
                return True
            
            import time
            return claims["exp"] < time.time()
        except Exception:
            return True