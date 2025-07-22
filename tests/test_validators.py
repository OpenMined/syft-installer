"""Unit tests for validators module."""
import pytest

from syft_installer._validators import (
    validate_email,
    validate_otp,
    sanitize_otp
)


class TestValidators:
    """Test validator functions."""
    
    def test_validate_email_valid(self):
        """Test valid email addresses."""
        valid_emails = [
            "user@example.com",
            "test.user@example.com",
            "user+tag@example.com",
            "user@subdomain.example.com",
            "123@example.com",
            "user@example.co.uk",
            "user_name@example.com",
            "user-name@example.com"
        ]
        
        for email in valid_emails:
            assert validate_email(email) is True, f"Expected {email} to be valid"
    
    def test_validate_email_invalid(self):
        """Test invalid email addresses."""
        invalid_emails = [
            "",
            "not-an-email",
            "@example.com",
            "user@",
            "user@@example.com",
            "user@example",
            "user @example.com",
            "user@example .com",
            " user@example.com",
            "user@example.com ",
            None
        ]
        
        for email in invalid_emails:
            assert validate_email(email) is False, f"Expected {email} to be invalid"
    
    def test_validate_otp_valid(self):
        """Test valid OTP codes."""
        valid_otps = [
            "ABCD1234",
            "12345678",
            "AAAAAAAA",
            "ZZZZZZZZ",
            "A1B2C3D4",
            "99999999"
        ]
        
        for otp in valid_otps:
            assert validate_otp(otp) is True, f"Expected {otp} to be valid"
    
    def test_validate_otp_invalid(self):
        """Test invalid OTP codes."""
        invalid_otps = [
            "",
            "abcd1234",  # lowercase
            "ABCD123",   # too short
            "ABCD12345", # too long
            "ABCD-123",  # invalid character
            "ABCD 234",  # space
            "ABCD_234",  # underscore
            "ABCD.234",  # period
            None
        ]
        
        for otp in invalid_otps:
            assert validate_otp(otp) is False, f"Expected {otp} to be invalid"
    
    def test_sanitize_otp(self):
        """Test OTP sanitization."""
        test_cases = [
            ("abcd1234", "ABCD1234"),
            ("ABCD1234", "ABCD1234"),
            (" ABCD1234 ", "ABCD1234"),
            ("  abcd1234  ", "ABCD1234"),
            ("ab cd 12 34", "ABCD1234"),
            ("a b c d 1 2 3 4", "ABCD1234"),
            ("", ""),
            ("   ", ""),
            ("aBcD1234", "ABCD1234")
        ]
        
        for input_otp, expected in test_cases:
            result = sanitize_otp(input_otp)
            assert result == expected, f"Expected sanitize_otp('{input_otp}') to return '{expected}', got '{result}'"
    
