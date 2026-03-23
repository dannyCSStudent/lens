# Phase 2 – Chronological Feed Endpoint

## Description

Build cursor-based `/posts/feed` returning `PostCard` entries honoring latest vs evidence_activity modes.

## Affected Backend Files

- apps/api/app/api/routes/posts.py
- apps/api/app/api/schemas/feed.py
- apps/api/app/services/post_service.py
- apps/api/app/core/enums.py

## Affected Frontend Files

- None

## Database Changes

Add nullable `trending_score` (for evidence activity) and covering index on `(status, created_at, id)`.

## API Endpoints

- GET /posts/feed

## Acceptance Criteria

- Feed returns deterministic ordering with `next_cursor`
- Mode defaults to latest when unspecified and never exposes engagement ranking
- Soft-deleted or unpublished posts never appear

## Test Requirements

- Service tests for cursor pagination
- API contract test verifying response schema and max limit enforcement

