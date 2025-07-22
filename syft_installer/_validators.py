import re
from email.utils import parseaddr


def validate_email(email: str) -> bool:
    r"""
    Validate email address.
    - Must pass RFC 5322 validation
    - Must match pattern: ^[^\s@]+@[^\s@]+\.[^\s@]+$
    """
    if not email:
        return False
    
    # RFC 5322 validation
    parsed = parseaddr(email)
    if not parsed[1] or parsed[1] != email:
        return False
    
    # Additional pattern validation
    pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    return bool(re.match(pattern, email))


def validate_otp(otp: str) -> bool:
    """
    Validate OTP code.
    - Must be exactly 8 characters
    - Must be uppercase alphanumeric only
    """
    if not otp:
        return False
    
    pattern = r"^[0-9A-Z]{8}$"
    return bool(re.match(pattern, otp))


def sanitize_otp(otp: str) -> str:
    """Convert OTP to uppercase and remove spaces."""
    return otp.strip().upper().replace(" ", "")