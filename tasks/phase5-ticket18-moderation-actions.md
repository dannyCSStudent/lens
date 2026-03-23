# Phase 5 – Moderation Actions & Audit Log

## Description

Provide admin routes to execute moderation actions with immutable audit entries and appeal hooks.

## Affected Backend Files

- apps/api/app/api/routes/admin_moderation.py
- apps/api/app/api/schemas/moderation.py
- apps/api/app/core/models/moderation.py
- apps/api/app/services/moderation_service.py

## Affected Frontend Files

- None

## Database Changes

Create `moderation_actions` table storing actor, action_type, subject refs, justification, appeal_state.

## API Endpoints

- POST /admin/moderation/actions
- POST /admin/moderation/appeals
- PATCH /admin/moderation/appeals/{id}

## Acceptance Criteria

- Only admins can access admin routes
- Every action logs immutable record
- Appeals update timestamps and cannot delete original action

## Test Requirements

- Role-based access tests
- Audit immutability test

