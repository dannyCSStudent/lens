# apps/api/app/core/enums.py

from enum import Enum

class PostType(str, Enum):
    expression = "expression"
    claim = "claim"
    investigation = "investigation"

class EvidenceDirection(str, Enum):
    supports = "supports"
    contradicts = "contradicts"

class ContentStatus(str, Enum):
    active = "active"
    locked = "locked"
    removed_illegal = "removed_illegal"


class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"

class FeedMode(str, Enum):
    latest = "latest"
    trending = "trending"


class SecurityEventType(str, Enum):
    login_success = "login_success"
    login_failed = "login_failed"
    account_locked = "account_locked"
    password_reset_requested = "password_reset_requested"
    password_reset_completed = "password_reset_completed"
    refresh_reuse_detected = "refresh_reuse_detected"
    session_revoked = "session_revoked"
    logout = "logout"
    refresh_token_reuse = "refresh_token_reuse"
    resend_verification = "resend_verification"
    suspicious_login_country = "suspicious_login_country"
    impossible_travel_login = "impossible_travel_login"
    suspicious_login_ip = "suspicious_login_ip"
    suspicious_login_device = "suspicious_login_device"
