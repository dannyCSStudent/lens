# Phase 6 – Notification Center UI

## Description

Implement notification inbox, bell badge, and background polling/websocket integration on the web app.

## Affected Backend Files

- None

## Affected Frontend Files

- apps/web/src/app/settings/notifications/page.tsx
- apps/web/src/app/components/NotificationBell.tsx
- apps/web/src/app/services/notifications.ts

## Database Changes

None

## API Endpoints

- GET /notifications
- POST /notifications/read

## Acceptance Criteria

- Bell badge reflects unread count and updates live
- Notifications page groups items by day with deep links
- Clicking an item marks it read

## Test Requirements

- Component tests for badge logic
- E2E verifying read/unread transitions

