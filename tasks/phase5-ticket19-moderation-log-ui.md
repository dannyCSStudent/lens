# Phase 5 – Public Moderation Log API & UI

## Description

Expose public moderation log endpoint with filters and build frontend page to display actions transparently.

## Affected Backend Files

- apps/api/app/api/routes/admin_moderation.py
- apps/api/app/api/schemas/moderation.py
- apps/api/app/services/moderation_service.py

## Affected Frontend Files

- apps/web/src/app/settings/moderation-log/page.tsx
- apps/web/src/app/services/moderation.ts
- apps/web/src/app/components/ModerationTable.tsx

## Database Changes

None (relies on moderation_actions table)

## API Endpoints

- GET /moderation/log

## Acceptance Criteria

- Endpoint returns paginated `{items, next_cursor}`
- Sensitive fields stripped for public consumers
- Frontend table supports filtering by action type/date

## Test Requirements

- API schema test for log endpoint
- Frontend test verifying pagination interaction

