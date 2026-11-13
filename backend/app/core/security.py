import hashlib
import secrets
import base64
import struct
from datetime import UTC, datetime, timedelta

from functools import cache

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from pydantic import SecretStr

password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except (InvalidHashError, VerificationError, VerifyMismatchError):
        return False


@cache
def dummy_password_hash() -> str:
    return password_hasher.hash(secrets.token_urlsafe(32))


def issue_access_token(
    user_id: str,
    secret_key: SecretStr,
    lifetime: timedelta,
) -> str:
    now = datetime.now(UTC)
    claims = {
        "sub": user_id,
        "iat": now,
        "exp": now + lifetime,
        "jti": secrets.token_urlsafe(16),
        "typ": "access",
    }
    return jwt.encode(claims, secret_key.get_secret_value(), algorithm="HS256")


def decode_access_token(token: str, secret_key: SecretStr) -> str | None:
    try:
        claims = jwt.decode(
            token,
            secret_key.get_secret_value(),
            algorithms=["HS256"],
            options={"require": ["sub", "exp", "iat", "typ"]},
        )
    except jwt.InvalidTokenError:
        return None
    if claims.get("typ") != "access":
        return None
    subject = claims.get("sub")
    return subject if isinstance(subject, str) else None


def create_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def utc_now_naive() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def otp_verify(secret: str, code: str, period: int = 30) -> bool:
    """Verify a TOTP (Time-based One-Time Password) code.
    
    Args:
        secret: The base32-encoded secret key
        code: The 6-digit code to verify
        period: The time period in seconds (default: 30)
        
    Returns:
        True if the code is valid, False otherwise
    """
    # Current time step
    time_step = int(datetime.now(UTC).timestamp() / period)
    
    # Calculate HMAC-SHA1
    secret_bytes = base64.b32decode(secret, case_insensitive=True)
    
    # Counter-based TOTP calculation
    import hmac
    message = struct.pack(">Q", time_step)
    hmac_hash = hmac.new(secret_bytes, message, hashlib.sha1).digest()
    
    # Dynamic truncation
    offset = hmac_hash[-1] & 0x0f
    binary = hmac_hash[offset:offset + 4]
    code_int = struct.unpack(">I", binary)[0] & 0x7fffffff
    
    # Generate the 6-digit code
    expected_code = code_int % 1000000
    
    # Format the expected code with leading zeros
    expected_str = f"{expected_code:06d}"
    
    return code == expected_str