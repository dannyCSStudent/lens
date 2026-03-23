# Phase 1 – Frontend Auth Experience

## Description

Deliver login/register/reset UI with validation, session-aware layouts, and auth guards for protected routes.

## Affected Backend Files

- None

## Affected Frontend Files

- apps/web/src/app/auth/page.tsx
- apps/web/src/app/layout.tsx
- apps/web/src/app/globals.css
- apps/web/src/app/services/auth.ts

## Database Changes

None

## API Endpoints

- POST /auth/register
- POST /auth/login
- POST /auth/logout
- POST /auth/verify-email

## Acceptance Criteria

- Unauthenticated users visiting `/` redirect to `/auth`
- Forms show inline validation + API errors
- Successful login stores session (HTTP-only cookie) and refreshes feed
- Logout clears client state and routes back to `/auth`

## Test Requirements

- Playwright flow covering register → mocked verify → login
- Component/unit tests for form validation logic

