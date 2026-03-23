# Phase 2 – Post Detail Retrieval API

## Description

Expose `/posts/{id}` returning author info, counters, and evidence summary for a single post.

## Affected Backend Files

- apps/api/app/api/routes/posts.py
- apps/api/app/services/post_service.py
- apps/api/app/api/schemas/post.py

## Affected Frontend Files

- None

## Database Changes

Optional: add slug or short id field for shareable URLs if needed.

## API Endpoints

- GET /posts/{id}

## Acceptance Criteria

- Returns 404 for missing/unpublished posts
- Includes aggregated counts and viewer like state
- Response schema matches contracts used by frontend

## Test Requirements

- API tests for happy path and unauthorized viewer
- Negative test ensuring drafts are hidden

