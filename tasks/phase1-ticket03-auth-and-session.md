# Phase 1 – Authentication & Session Management API

## Description

Implement register/login/logout/refresh/email verification flows with rate limiting, refresh-token revocation, and security event logging.

## Affected Backend Files

- apps/api/app/api/routes/auth.py
- apps/api/app/api/schemas/auth.py
- apps/api/app/services/security_service.py
- apps/api/app/core/security.py
- apps/api/app/core/models/refresh_token.py
- apps/api/app/core/models/email_verification_token.py
- apps/api/app/core/cache/redis.py

## Affected Frontend Files

- None

## Database Changes

Add `refresh_tokens` and `email_verification_tokens` tables with hashed token storage, expirations, and indexes for lookups.

## API Endpoints

- POST /auth/register
- POST /auth/login
- POST /auth/logout
- POST /auth/refresh
- POST /auth/verify-email
- POST /auth/resend-verification

## Acceptance Criteria

- Rate limits enforced on auth routes via SlowAPI
- Refresh tokens can be revoked and blocked via Redis
- Security events recorded for failed logins and lockouts

## Test Requirements

- API tests covering successful flows plus invalid password, unverified user, expired refresh token
- Cache-layer test ensuring revoked session IDs cannot refresh

