# Phase 4 – Global Rate Limiting & Abuse Controls

## Description

Enforce request-level and action-specific rate limits with anomaly logging and lockouts.

## Affected Backend Files

- apps/api/app/core/rate_limit.py
- apps/api/app/main.py
- apps/api/app/core/securities/login_detection.py
- apps/api/app/services/security_service.py

## Affected Frontend Files

- None

## Database Changes

None

## API Endpoints

- All write endpoints including /posts, /replies, /evidence, /reports

## Acceptance Criteria

- Exceeding per-endpoint limits returns 429 with standardized payload
- Lockouts recorded in security_event table with expiry
- Config allows tuning per route without redeploy

## Test Requirements

- SlowAPI-based tests asserting rate limit headers
- Lockout expiry test

