# Phase 2 – Post Creation Domain Model

## Description

Implement `Post` schema, enums, and service logic for expression/claim/investigation types with counters and status tracking.

## Affected Backend Files

- apps/api/app/core/models/post.py
- apps/api/app/api/schemas/post.py
- apps/api/app/services/post_service.py
- apps/api/alembic/versions/xxxx_create_posts.py

## Affected Frontend Files

- None

## Database Changes

Create `posts` table with post_type/status enums, counters (reply/evidence/like), timestamps, and soft-delete markers.

## API Endpoints

- None

## Acceptance Criteria

- Migration creates table with default counters set to 0
- Service enforces valid post types and prevents hard deletes
- Posts persist with published status by default

## Test Requirements

- Schema validation unit tests
- Service test ensuring investigations obey content limits

