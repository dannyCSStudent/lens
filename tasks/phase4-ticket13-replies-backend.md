# Phase 4 – Replies Domain & API

## Description

Implement threaded replies with parent-child relationships, depth limits, and soft deletes.

## Affected Backend Files

- apps/api/app/api/routes/replies.py
- apps/api/app/api/schemas/reply.py
- apps/api/app/core/models/reply.py
- apps/api/app/services/reply_service.py

## Affected Frontend Files

- None

## Database Changes

Create `replies` table referencing posts and parent replies, storing depth, path tokens, and moderation status.

## API Endpoints

- POST /replies
- GET /posts/{post_id}/replies

## Acceptance Criteria

- API rejects replies beyond depth limit
- Replies inherit post visibility and soft-delete behavior
- List endpoint returns tree ordered chronologically

## Test Requirements

- API tests for nested replies and depth guard
- Service tests for tree serialization

