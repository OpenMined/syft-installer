"""Unit tests for authentication module."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import jwt
from datetime import datetime, timedelta

from syft_installer.auth import Authenticator
from syft_installer.exceptions import OTPError, TokenError


class TestAuthenticator:
    """Test Authenticator class."""
    
    def test_init(self):
        """Test authenticator initialization."""
        auth = Authenticator()
        assert auth.server_url == "https://syftbox.net"
        
        auth = Authenticator("https://custom.server.com")
        assert auth.server_url == "https://custom.server.com"
        
        # Test trailing slash removal
        auth = Authenticator("https://server.com/")
        assert auth.server_url == "https://server.com"
    
    @patch('requests.post')
    def test_request_otp_success(self, mock_post):
        """Test successful OTP request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "otp_sent"}
        mock_post.return_value = mock_response
        
        auth = Authenticator()
        result = auth.request_otp("test@example.com")
        
        assert result == {"status": "otp_sent"}
        mock_post.assert_called_once_with(
            "https://syftbox.net/auth/otp/request",
            json={"email": "test@example.com"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
    
    @patch('requests.post')
    def test_request_otp_failure(self, mock_post):
        """Test failed OTP request."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid email"
        mock_post.return_value = mock_response
        
        auth = Authenticator()
        with pytest.raises(OTPError, match="OTP request failed"):
            auth.request_otp("invalid")
    
    @patch('requests.post')
    def test_verify_otp_success(self, mock_post):
        """Test successful OTP verification."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token"
        }
        mock_post.return_value = mock_response
        
        auth = Authenticator()
        tokens = auth.verify_otp("test@example.com", "ABCD1234")
        
        assert tokens["access_token"] == "test_access_token"
        assert tokens["refresh_token"] == "test_refresh_token"
        mock_post.assert_called_once_with(
            "https://syftbox.net/auth/otp/verify",
            json={"email": "test@example.com", "code": "ABCD1234"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
    
    @patch('requests.post')
    def test_verify_otp_failure(self, mock_post):
        """Test failed OTP verification."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Invalid OTP"
        mock_post.return_value = mock_response
        
        auth = Authenticator()
        with pytest.raises(OTPError, match="OTP verification failed"):
            auth.verify_otp("test@example.com", "WRONG123")
    
    @patch('requests.post')
    def test_refresh_token_success(self, mock_post):
        """Test successful token refresh."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token"
        }
        mock_post.return_value = mock_response
        
        auth = Authenticator()
        tokens = auth.refresh_token("old_refresh_token")
        
        assert tokens["access_token"] == "new_access_token"
        assert tokens["refresh_token"] == "new_refresh_token"
        mock_post.assert_called_once_with(
            "https://syftbox.net/auth/refresh",
            json={"refresh_token": "old_refresh_token"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
    
    @patch('requests.post')
    def test_refresh_token_failure(self, mock_post):
        """Test failed token refresh."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Invalid refresh token"
        mock_post.return_value = mock_response
        
        auth = Authenticator()
        with pytest.raises(TokenError, match="Token refresh failed"):
            auth.refresh_token("invalid_token")
    
    def test_decode_token(self):
        """Test JWT token decoding."""
        auth = Authenticator()
        
        # Create a test token
        payload = {
            "sub": "test@example.com",
            "type": "access",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        secret = "test_secret"
        token = jwt.encode(payload, secret, algorithm="HS256")
        
        # Decode without verification
        claims = auth.decode_token(token)
        assert claims["sub"] == "test@example.com"
        assert claims["type"] == "access"
    
    @patch('requests.post')
    def test_request_otp_connection_error(self, mock_post):
        """Test OTP request with connection error."""
        mock_post.side_effect = Exception("Connection failed")
        
        auth = Authenticator()
        with pytest.raises(OTPError, match="OTP request error"):
            auth.request_otp("test@example.com")
    
    @patch('requests.post')
    def test_verify_otp_connection_error(self, mock_post):
        """Test OTP verification with connection error."""
        mock_post.side_effect = Exception("Connection failed")
        
        auth = Authenticator()
        with pytest.raises(OTPError, match="OTP verification error"):
            auth.verify_otp("test@example.com", "ABCD1234")