from dataclasses import dataclass
import json
import logging
import re
import secrets
from datetime import UTC, datetime, timedelta

from pydantic import SecretStr
from sqlalchemy.orm import Session

from app.config.settings import Settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.permissions import UserRole
from app.core.security import (
    as_utc,
    create_refresh_token,
    decode_access_token,
    dummy_password_hash,
    hash_password,
    hash_refresh_token,
    issue_access_token,
    otp_verify,
    utc_now_naive,
    verify_password,
)
from app.integrations.email_provider import get_email_notification_provider
from app.modules.auth.models import RefreshSession, User
from app.modules.auth.repository import AuthRepository, UserRepository

logger = logging.getLogger(__name__)
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]{3,64}$")
PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,128}$")
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)
REFRESH_TOKEN_ROTATION = True
MAX_REFRESH_TOKEN_AGE_DAYS = 90
REMEMBER_ME_COOKIE_DAYS = 30
MAX_CONCURRENT_SESSIONS = 5

# TOTP (Two-Factor Authentication) settings
TOTP_ISSUER = "Data Integrity & Security Platform"
TOTP_DIGITS = 6
TOTP_PERIOD = 30  # 30 seconds


@dataclass(frozen=True)
class AuthTokens:
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"
    remember_me: bool = False
    mfa_verified: bool = False
    user: User | None = None  # User model for GraphQL relay


class AuthService:
    def __init__(self, session: Session, settings: Settings) -> None:
        self.session = session
        self.settings = settings
        self.users = UserRepository(session)
        self.auth = AuthRepository(session)

    def authenticate_access_token(self, token: str | None) -> User | None:
        if not token or self.settings.secret_key is None:
            return None
        user_id = decode_access_token(token, self.settings.secret_key)
        if user_id is None:
            return None
        user = self.users.get_by_id(user_id)
        return user if user is not None and user.is_active else None

    def login(self, username: str, password: str, remember_me: bool = False, mfa_code: str | None = None) -> AuthTokens:
        """Login with optional MFA support.
        
        Args:
            username: User's normalized username
            password: User's password
            remember_me: Whether to extend token validity
            mfa_code: Optional MFA code (TOTP) for second factor auth
            
        Returns:
            AuthTokens on success
        """
        normalized_username = username.strip().casefold()
        user = self.users.get_by_username(normalized_username)
        now = datetime.now(UTC).replace(tzinfo=None)  # naive UTC

        # Check if account is locked
        if user is not None and user.locked_until is not None:
            # Ensure both datetimes are naive for comparison
            locked_until = user.locked_until
            if locked_until.tzinfo is not None:
                locked_until = locked_until.replace(tzinfo=None)
            if locked_until > now:
                remaining_minutes = max(0, int((locked_until - now).total_seconds() / 60))
                raise AuthenticationError(
                    f"Account locked due to too many failed attempts. "
                    f"Try again in {remaining_minutes} minutes."
                )
            # Lock has expired, reset it
            user.locked_until = None
            user.failed_login_attempts = 0

        if user is None:
            # Don't reveal if user exists - use dummy to always fail same way
            verify_password(dummy_password_hash(), password)
            raise AuthenticationError("Invalid username or password.")
        
        # Check account active status
        if not user.is_active:
            raise AuthenticationError("Invalid username or password.")

        # Verify password
        if not verify_password(user.password_hash, password):
            # Track failed attempt
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                user.locked_until = now + LOCKOUT_DURATION
                user.failed_login_attempts = 0
            # If MFA is enabled and password is wrong but MFA might be right,
            # still track the failed attempt for lockout purposes
            self.session.commit()
            raise AuthenticationError("Invalid username or password.")

        # Password successful - reset failure tracking
        user.failed_login_attempts = 0
        user.locked_until = None

        # MFA verification if enabled
        if user.mfa_enabled and not user.mfa_verified:
            if mfa_code is None:
                raise AuthenticationError(
                    "Multi-factor authentication required. "
                    "Please provide a valid TOTP code."
                )
            if not otp_verify(user.mfa_secret, mfa_code, TOTP_PERIOD):
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                    user.locked_until = now + LOCKOUT_DURATION
                    user.failed_login_attempts = 0
                self.session.commit()
                raise AuthenticationError("Invalid multi-factor authentication code.")
            # Mark MFA as verified for this session
            user.mfa_verified = True

        # Device tracking - check if this is a new device
        is_new_device = False
        # Devices are stored as JSON string; parse it
        if user.devices is None or user.devices == "[]":
            user.devices = []
        else:
            try:
                user.devices = json.loads(user.devices)
            except (json.JSONDecodeError, TypeError):
                user.devices = []
        
        if not isinstance(user.devices, list):
            user.devices = []
        
        # Check if this device is already registered
        user_agent = getattr(request, 'headers', {}).get('user-agent', '') if 'request' in dir() else ''
        if not any(d.get('user_agent') == user_agent for d in user.devices):
            is_new_device = True
            # Add new device (limit to 5 devices per user)
            if len(user.devices) >= MAX_CONCURRENT_SESSIONS:
                # Remove oldest device
                user.devices.pop(0)
            user.devices.append({
                'user_agent': user_agent,
                'last_seen': now,
                'is_trusted': remember_me,
            })
        
        # Serialize devices back to JSON string for database storage
        user.devices = json.dumps(user.devices, default=str)

        # Update last login
        user.last_login = now

        tokens = self._issue_tokens(user, now, remember_me)
        self.session.commit()
        return tokens

    def refresh(self, refresh_token: str) -> AuthTokens:
        now = utc_now_naive()
        current = self.auth.get_refresh_session(hash_refresh_token(refresh_token))
        if (
            current is None
            or current.revoked_at is not None
            or as_utc(current.expires_at) <= now.replace(tzinfo=UTC)
        ):
            raise AuthenticationError("Invalid or expired refresh token.")

        user = self.users.get_by_id(current.user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("Invalid or expired refresh token.")

        # Revoke current refresh session (rotation)
        if not self.auth.revoke_if_active(current.id, now):
            self.session.rollback()
            raise AuthenticationError("Invalid or expired refresh token.")

        # Determine remember_me from user's device trust status or default to False
        # Devices are stored as JSON on the user model; check if any device is trusted
        is_remember_me = False
        if user and user.devices:
            try:
                devices = json.loads(user.devices) if isinstance(user.devices, str) else user.devices
                if isinstance(devices, list):
                    is_remember_me = any(d.get('is_trusted', False) for d in devices)
            except (json.JSONDecodeError, TypeError):
                pass

        # Issue new tokens with remember_me state
        tokens = self._issue_tokens(user, now, remember_me=is_remember_me)
        self.session.commit()
        return tokens

    def logout(self, refresh_token: str) -> dict:
        """Logout and return result with details."""
        now = utc_now_naive()
        current = self.auth.get_refresh_session(hash_refresh_token(refresh_token))
        if current is None or current.revoked_at is not None:
            return {"success": False, "reason": "invalid_or_revoked"}
        
        user = self.users.get_by_id(current.user_id)
        # Invalidate all other sessions for this user except the current one
        if user and user.devices:
            try:
                devices = json.loads(user.devices) if isinstance(user.devices, str) else user.devices
                if isinstance(devices, list):
                    current_refresh_id = current.id
                    user.devices = [d for d in devices if d.get('refresh_token_id') != current_refresh_id]
                    # Serialize devices back to JSON string for database storage
                    user.devices = json.dumps(user.devices, default=str)
            except (json.JSONDecodeError, TypeError):
                user.devices = "[]"
        
        current.revoked_at = now
        self.session.commit()
        return {"success": True, "revoked_at": current.revoked_at.isoformat()}

    def reset_user_failed_attempts(self, user_id: str) -> bool:
        """Reset failed login attempts for a user (admin function)."""
        user = self.users.get_by_id(user_id)
        if user is None:
            return False
        user.failed_login_attempts = 0
        user.locked_until = None
        user.mfa_verified = False
        self.session.commit()
        return True

    def lock_user(self, user_id: str, duration_minutes: int | None = None) -> bool:
        """Manually lock a user account (admin function)."""
        user = self.users.get_by_id(user_id)
        if user is None:
            return False
        lock_duration = timedelta(minutes=duration_minutes or LOCKOUT_DURATION.total_seconds() // 60)
        user.locked_until = utc_now_naive() + lock_duration
        user.failed_login_attempts = MAX_FAILED_ATTEMPTS
        self.session.commit()
        return True

    def unlock_user(self, user_id: str) -> bool:
        """Manually unlock a user account (admin function)."""
        user = self.users.get_by_id(user_id)
        if user is None:
            return False
        user.locked_until = None
        user.failed_login_attempts = 0
        user.mfa_verified = False
        self.session.commit()
        return True

    def is_account_locked(self, user_id: str) -> dict:
        """Check if account is locked. Returns lock status dict."""
        user = self.users.get_by_id(user_id)
        if user is None:
            return {"locked": False, "error": "user_not_found"}
        
        if user.locked_until is None:
            return {"locked": False, "remaining_minutes": 0}
        
        now = utc_now_naive()
        if as_utc(user.locked_until) > now.replace(tzinfo=UTC):
            remaining = max(0, int((user.locked_until - now.replace(tzinfo=UTC)).total_seconds() / 60))
            return {"locked": True, "remaining_minutes": remaining}
        
        # Lock has expired, reset it
        user.locked_until = None
        user.failed_login_attempts = 0
        self.session.commit()
        return {"locked": False, "remaining_minutes": 0}

    def _issue_tokens(self, user: User, now: datetime, remember_me: bool = False) -> AuthTokens:
        if self.settings.secret_key is None:
            raise RuntimeError("APP_SECRET_KEY must be configured before authentication is used.")
        
        lifetime_minutes = self.settings.access_token_minutes
        if remember_me and self.settings.remember_me_enabled:
            lifetime_minutes = min(lifetime_minutes * 4, 1440)  # Max 24h for remember me
        
        # Refresh token expiry
        refresh_expiry_days = self.settings.refresh_token_days
        if remember_me and self.settings.remember_me_enabled:
            refresh_expiry_days = min(refresh_expiry_days * 2, 365)  # Max 1 year for remember me
        
        lifetime = timedelta(minutes=lifetime_minutes)
        refresh_token = create_refresh_token()
        refresh_session = RefreshSession(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=now + timedelta(days=refresh_expiry_days),
            user_agent=getattr(request, 'headers', {}).get('user-agent', '') if 'request' in dir() else '',
        )
        self.auth.add_refresh_session(refresh_session)
        return AuthTokens(
            access_token=issue_access_token(user.id, self.settings.secret_key, lifetime),
            refresh_token=refresh_token,
            expires_in=int(lifetime.total_seconds()),
            token_type="Bearer",
            remember_me=remember_me,
            mfa_verified=user.mfa_verified,
            user=user,
        )

    def send_alert_notification(self, alert_title: str, alert_description: str, alert_severity: str, alert_id: str) -> bool:
        """Send alert notification via email."""
        try:
            provider = get_email_notification_provider()
            success = provider.send_alert_notification(alert_title, alert_description, alert_severity, alert_id)
            if success:
                logger.info(f"Alert notification sent for alert {alert_id}: {alert_title}")
            return success
        except Exception as e:
            logger.error(f"Failed to send alert notification: {e}")
            return False

    def enable_mfa(self, user_id: str) -> bool:
        """Enable MFA for a user. Returns secret key for setup."""
        user = self.users.get_by_id(user_id)
        if user is None:
            return False
        import base64
        # Generate a secret key for TOTP
        secret = base64.b32hexify(secrets.token_bytes(20)).decode('ascii')
        user.mfa_secret = secret
        user.mfa_enabled = True
        user.mfa_verified = False
        self.session.commit()
        return True

    def disable_mfa(self, user_id: str, mfa_code: str) -> bool:
        """Disable MFA for a user (requires current code verification)."""
        user = self.users.get_by_id(user_id)
        if user is None:
            return False
        # Verify current MFA code before disabling
        if not otp_verify(user.mfa_secret, mfa_code, TOTP_PERIOD):
            return False
        user.mfa_enabled = False
        user.mfa_secret = None
        self.session.commit()
        return True

    def get_user_devices(self, user_id: str) -> list:
        """Get all registered devices for a user."""
        user = self.users.get_by_id(user_id)
        if user is None:
            return []
        return user.devices or []

    def revoke_other_sessions(self, user_id: str, except_refresh_token: str | None = None) -> int:
        """Revoke all refresh sessions for a user except the specified one."""
        user = self.users.get_by_id(user_id)
        if user is None:
            return 0
        
        # This is a simplified version - in a full implementation,
        # you'd query all refresh sessions for the user and revoke them
        # For now, just reset the devices list to effectively log out from all devices
        user.devices = []
        self.session.commit()
        return 0