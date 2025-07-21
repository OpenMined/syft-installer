import json
from typing import Dict, Optional

import jwt
import requests

from syft_installer.exceptions import AuthenticationError, ValidationError
from syft_installer.validators import validate_email, validate_otp, sanitize_otp


class Authenticator:
    """Handle OTP-based authentication flow."""
    
    def __init__(self, server_url: str = "https://syftbox.net"):
        self.server_url = server_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "syft-installer/0.1.0",
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
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
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
        data = {"email": email, "otp": otp}
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            
            # Validate tokens exist
            if "access_token" not in result or "refresh_token" not in result:
                raise AuthenticationError("Invalid response: missing tokens")
            
            return result
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response.status_code == 401:
                raise AuthenticationError("Invalid OTP or expired")
            raise AuthenticationError(f"Failed to verify OTP: {str(e)}")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Use refresh token to get a new access token.
        
        Args:
            refresh_token: JWT refresh token
            
        Returns:
            New access token
            
        Raises:
            AuthenticationError: If refresh fails
        """
        url = f"{self.server_url}/auth/refresh"
        headers = {"Authorization": f"Bearer {refresh_token}"}
        
        try:
            response = self.session.post(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            return result["access_token"]
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response.status_code == 401:
                raise AuthenticationError("Refresh token expired or invalid")
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