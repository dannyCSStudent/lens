# Phase 5 – Reporting Workflow Backend

## Description

Enable structured user reports with immutable records and moderator triage fields.

## Affected Backend Files

- apps/api/app/api/routes/reports.py
- apps/api/app/api/schemas/report.py
- apps/api/app/core/models/report.py
- apps/api/app/services/moderation_service.py

## Affected Frontend Files

- None

## Database Changes

Create `reports` table capturing reporter, target entity, reason enum, status, resolution timestamps.

## API Endpoints

- POST /reports
- GET /reports/{id}
- GET /reports

## Acceptance Criteria

- Duplicate spam prevented via rate limits
- Reporter sees only their own submissions
- Moderator queries filter by status without exposing sensitive fields

## Test Requirements

- API tests for permissions
- Service tests for status transitions

