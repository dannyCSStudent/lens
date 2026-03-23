# Phase 6 – Notification Infrastructure

## Description

Persist notifications for mentions, replies, and moderation outcomes plus APIs to fetch and mark read.

## Affected Backend Files

- apps/api/app/core/models/notification.py
- apps/api/app/api/schemas/notification.py
- apps/api/app/services/notification_service.py
- apps/api/app/api/routes/notifications.py

## Affected Frontend Files

- None

## Database Changes

Create `notifications` table with type, payload JSON, read_at, and indexes per user.

## API Endpoints

- GET /notifications
- POST /notifications/read
- GET /notifications/unread-count

## Acceptance Criteria

- Notifications created for replies/mentions/moderation actions
- Unread counts accurate and update when marking read
- Background jobs handle fan-out without blocking requests

## Test Requirements

- Service tests generating notifications from events
- API pagination and mark-read tests

