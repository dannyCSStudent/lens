# Phase 5 – Report & Safety UI Hooks

## Description

Add report dialog, moderator dashboard links, and lock banners on moderated posts.

## Affected Backend Files

- None

## Affected Frontend Files

- apps/web/src/app/components/ReportDialog.tsx
- apps/web/src/app/posts/[id]/page.tsx
- apps/web/src/app/services/reports.ts
- apps/web/src/app/settings/moderation/page.tsx

## Database Changes

None

## API Endpoints

- POST /reports
- GET /moderation/log

## Acceptance Criteria

- Report dialog enforces category selection and surfaces success/failure
- Moderators have navigation entry to moderation log
- Posts locked by moderation display clear banner

## Test Requirements

- UI test submitting report and seeing confirmation
- Snapshot/unit test for lock banner

