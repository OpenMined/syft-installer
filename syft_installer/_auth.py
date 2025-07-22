from typing import Dict

import jwt
import requests

from syft_installer._utils import AuthenticationError, ValidationError, validate_email, validate_otp, sanitize_otp


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
        
        try:
            response = self.session.post(url, json=data, timeout=30)
            response.raise_for_status()
            
            # OTP request returns empty body on success
            return {"status": "success", "message": "OTP sent to email"}
                
        except requests.exceptions.RequestException as e:
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
    
