# Phase 6 – Pagination Consistency Audit

## Description

Ensure every listing endpoint uses cursor pagination with uniform response envelopes and validation.

## Affected Backend Files

- apps/api/app/api/routes/posts.py
- apps/api/app/api/routes/replies.py
- apps/api/app/api/routes/evidence.py
- apps/api/app/api/routes/notifications.py
- apps/api/app/api/routes/reports.py

## Affected Frontend Files

- apps/web/src/app/services/feed.ts
- apps/web/src/app/services/replies.ts
- apps/web/src/app/services/evidence.ts
- apps/web/src/app/services/notifications.ts

## Database Changes

None

## API Endpoints

- GET /posts/feed
- GET /posts/{id}/replies
- GET /evidence/post/{post_id}
- GET /notifications
- GET /reports

## Acceptance Criteria

- All list endpoints return `{items, next_cursor}` schema
- Opaque base64 cursors validated and return 400 on invalid input
- Frontend services handle shared pagination contract

## Test Requirements

- API contract tests per endpoint
- Frontend service tests ensuring cursor reuse works

